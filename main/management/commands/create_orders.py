# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random
from faker import Faker

from main.models import Order, OrderItem, ClassifiedAd, User


class Command(BaseCommand):
    help = "Create sample orders for existing ads"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=50,
            help="Number of orders to create (default: 50)",
        )
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Spread orders over this many days (default: 30)",
        )

    def handle(self, *args, **options):
        count = options["count"]
        days = options["days"]

        fake = Faker(["ar_EG", "en_US"])

        # Get existing users and ads
        users = list(User.objects.filter(is_active=True).exclude(is_staff=True))
        ads = list(ClassifiedAd.objects.filter(status="active"))

        if not users:
            self.stdout.write(
                self.style.ERROR("No users found! Please create users first.")
            )
            return

        if not ads:
            self.stdout.write(
                self.style.ERROR("No active ads found! Please create ads first.")
            )
            return

        self.stdout.write(
            f"Creating {count} orders from {len(ads)} ads for {len(users)} users..."
        )

        created_count = 0
        for i in range(count):
            try:
                # Random user
                user = random.choice(users)

                # Random date within the last X days
                days_ago = random.randint(0, days)
                order_date = timezone.now() - timedelta(days=days_ago)

                # Random status
                status_choices = [
                    "pending",
                    "processing",
                    "shipped",
                    "delivered",
                    "cancelled",
                ]
                status = random.choice(status_choices)

                # Older orders are more likely to be delivered
                if days_ago > 7:
                    status = random.choice(
                        ["delivered", "delivered", "delivered", "cancelled", "shipped"]
                    )
                elif days_ago > 3:
                    status = random.choice(["processing", "shipped", "delivered"])

                # Payment method
                payment_method = random.choice(["cod", "online", "partial"])

                # Calculate delivery fee first
                delivery_fee = Decimal(random.choice([0, 10, 15, 20, 25]))

                # Create order with initial values
                order = Order.objects.create(
                    user=user,
                    full_name=(
                        f"{user.first_name} {user.last_name}"
                        if user.first_name
                        else user.username
                    ),
                    phone=user.phone or fake.phone_number(),
                    address=fake.address(),
                    city=random.choice(
                        [
                            "الرياض",
                            "جدة",
                            "الدمام",
                            "مكة",
                            "المدينة",
                            "القصيم",
                            "الطائف",
                        ]
                    ),
                    postal_code=fake.postcode(),
                    notes=fake.text(max_nb_chars=100) if random.random() > 0.7 else "",
                    payment_method=payment_method,
                    status=status,
                    delivery_fee=delivery_fee,
                    total_amount=Decimal("0.00"),  # Will update after adding items
                    paid_amount=Decimal("0.00"),  # Will update based on status
                    created_at=order_date,
                    updated_at=order_date,
                )

                # Add random items (1-5 items per order)
                num_items = random.randint(1, 5)
                selected_ads = random.sample(ads, min(num_items, len(ads)))

                total_amount = Decimal("0.00")
                for ad in selected_ads:
                    # Handle None price - use a default or skip
                    if ad.price is None:
                        price = Decimal("100.00")
                    else:
                        price = Decimal(str(ad.price))

                    OrderItem.objects.create(
                        order=order, ad=ad, price=price
                    )
                    total_amount += price

                # Add delivery fee
                total_amount += delivery_fee

                # Set payment amounts
                order.total_amount = total_amount

                if payment_method == "partial":
                    # Paid 30-70% of total
                    order.paid_amount = total_amount * Decimal(random.uniform(0.3, 0.7))
                elif status in ["delivered", "shipped", "processing"]:
                    # Mostly paid
                    if random.random() > 0.2:
                        order.paid_amount = total_amount
                    else:
                        order.paid_amount = total_amount * Decimal(
                            random.uniform(0.5, 0.9)
                        )
                elif status == "cancelled":
                    # Some cancelled orders might have partial payments
                    if random.random() > 0.7:
                        order.paid_amount = total_amount * Decimal(
                            random.uniform(0.2, 0.5)
                        )
                else:
                    # Pending orders - mostly unpaid or partial
                    if random.random() > 0.5:
                        order.paid_amount = Decimal("0.00")
                    else:
                        order.paid_amount = total_amount * Decimal(
                            random.uniform(0.2, 0.4)
                        )

                # Set expiration for pending COD orders
                if status == "pending" and payment_method == "cod":
                    if random.random() > 0.5:
                        try:
                            order.expires_at = order_date + timedelta(
                                hours=random.randint(24, 72)
                            )
                        except Exception as exp_error:
                            self.stdout.write(
                                self.style.ERROR(
                                    f"Error setting expires_at: {exp_error}, order_date={order_date}"
                                )
                            )
                            pass

                order.save()
                created_count += 1

                if (i + 1) % 10 == 0:
                    self.stdout.write(f"Created {i + 1}/{count} orders...")

            except Exception as e:
                import traceback

                self.stdout.write(self.style.WARNING(f"Error creating order: {str(e)}"))
                self.stdout.write(self.style.WARNING(traceback.format_exc()))

        self.stdout.write(
            self.style.SUCCESS(f"\nSuccessfully created {created_count} orders!")
        )
