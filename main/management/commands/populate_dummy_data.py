import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from main.models import (
    AdPackage,
    AdReport,
    AdReservation,
    AdReview,
    ClassifiedAd,
    Payment,
    User,
    UserPackage,
)


class Command(BaseCommand):
    """
    A custom management command to populate the database with dummy data
    for AdReview, AdReport, UserPackage, and AdReservation models.

    Example usage:
    python manage.py populate_dummy_data --reviews 50 --reports 30 --packages 20 --reservations 40
    python manage.py populate_dummy_data --all 100
    """

    help = "Populates the database with dummy data for reviews, reports, user packages, and reservations."

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--reviews",
            type=int,
            default=0,
            help="Number of ad reviews to create",
        )
        parser.add_argument(
            "--reports",
            type=int,
            default=0,
            help="Number of ad reports to create",
        )
        parser.add_argument(
            "--packages",
            type=int,
            default=0,
            help="Number of user packages to create",
        )
        parser.add_argument(
            "--reservations",
            type=int,
            default=0,
            help="Number of ad reservations to create",
        )
        parser.add_argument(
            "--all",
            type=int,
            help="Create equal number of all types (overrides individual counts)",
        )

    def handle(self, *args, **kwargs):
        """The main logic for the command."""
        fake = Faker(["ar_EG", "en_US"])  # Use Arabic and English locales

        # Determine counts
        if kwargs["all"]:
            review_count = report_count = package_count = reservation_count = kwargs["all"]
        else:
            review_count = kwargs["reviews"]
            report_count = kwargs["reports"]
            package_count = kwargs["packages"]
            reservation_count = kwargs["reservations"]

        # Get existing data
        users = list(User.objects.all())
        ads = list(ClassifiedAd.objects.all())
        packages = list(AdPackage.objects.all())

        if not users:
            self.stdout.write(
                self.style.ERROR("No users found! Please create users first.")
            )
            return

        if not ads and (review_count > 0 or reservation_count > 0):
            self.stdout.write(
                self.style.WARNING(
                    "No ads found! Skipping review and reservation creation. Please create ads first."
                )
            )
            review_count = 0
            reservation_count = 0

        if not ads and report_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    "No ads found! Ad reports will only include user reports."
                )
            )

        if not packages and package_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    "No packages found! Skipping package creation. Please create ad packages first."
                )
            )
            package_count = 0

        # Create reviews
        if review_count > 0:
            created_reviews = self._create_reviews(
                fake, users, ads, review_count
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created {created_reviews} ad reviews."
                )
            )

        # Create reports
        if report_count > 0:
            created_reports = self._create_reports(
                fake, users, ads, report_count
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created {created_reports} ad reports."
                )
            )

        # Create user packages
        if package_count > 0:
            created_packages = self._create_user_packages(
                fake, users, packages, package_count
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created {created_packages} user packages."
                )
            )

        # Create reservations
        if reservation_count > 0:
            created_reservations = self._create_reservations(
                fake, users, ads, reservation_count
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created {created_reservations} ad reservations."
                )
            )

        self.stdout.write(
            self.style.SUCCESS("\n[SUCCESS] Dummy data population completed!")
        )

    def _create_reviews(self, fake, users, ads, count):
        """Create dummy ad reviews."""
        created = 0
        self.stdout.write(f"\nCreating {count} ad reviews...")

        # List of sample Arabic comments
        arabic_comments = [
            "منتج ممتاز وجودة عالية",
            "البائع محترم جداً وسريع في الرد",
            "السعر مناسب والمنتج كما في الوصف",
            "تجربة رائعة، أنصح بالتعامل",
            "خدمة ممتازة ومنتج أصلي",
            "استلمت المنتج بسرعة وحالة ممتازة",
            "البائع أمين وصادق في التعامل",
            "المنتج مطابق للمواصفات تماماً",
            "تعامل راقي ومحترم",
            "جودة عالية وسعر تنافسي",
        ]

        for i in range(count):
            try:
                user = random.choice(users)
                ad = random.choice(ads)
                rating = random.choices(
                    [1, 2, 3, 4, 5],
                    weights=[5, 10, 15, 30, 40],  # More positive ratings
                    k=1,
                )[0]

                # Use Arabic comments or generate fake ones
                if random.random() > 0.5:
                    comment = random.choice(arabic_comments)
                else:
                    comment = fake.sentence(nb_words=10)

                # 90% approved, 10% not approved
                is_approved = random.random() > 0.1

                review = AdReview.objects.create(
                    ad=ad,
                    user=user,
                    rating=rating,
                    comment=comment,
                    is_approved=is_approved,
                )

                # Randomize created_at to simulate historical data
                days_ago = random.randint(1, 180)
                review.created_at = timezone.now() - timedelta(days=days_ago)
                review.save(update_fields=["created_at"])

                created += 1
                # Encode title safely for Windows console
                try:
                    title_preview = ad.title[:30]
                    title_preview.encode('cp1252')
                except (UnicodeEncodeError, AttributeError):
                    title_preview = "Ad"
                self.stdout.write(
                    f"  [OK] Created review #{i+1}: {user.username} -> {title_preview}... ({rating} stars)"
                )

            except Exception as e:
                # Skip if review already exists (unique constraint)
                self.stdout.write(
                    self.style.WARNING(
                        f"  [SKIP] Skipping review #{i+1}: {str(e)}"
                    )
                )

        return created

    def _create_reports(self, fake, users, ads, count):
        """Create dummy ad reports."""
        created = 0
        self.stdout.write(f"\nCreating {count} ad reports...")

        # Sample Arabic descriptions
        arabic_descriptions = [
            "هذا الإعلان يحتوي على معلومات مضللة",
            "المنتج المعروض غير متوفر فعلياً",
            "البائع لا يرد على الرسائل",
            "الصور مسروقة من مواقع أخرى",
            "السعر المذكور غير صحيح",
            "هذا إعلان متكرر",
            "معلومات الاتصال غير صحيحة",
            "محتوى غير لائق",
            "القسم غير مناسب للمنتج",
            "محاولة احتيال واضحة",
        ]

        report_types = [choice[0] for choice in AdReport.ReportType.choices]
        statuses = [choice[0] for choice in AdReport.Status.choices]

        for i in range(count):
            try:
                reporter = random.choice(users)
                report_type = random.choice(report_types)

                # 70% ad reports, 30% user reports
                if ads and random.random() > 0.3:
                    reported_ad = random.choice(ads)
                    reported_user = None
                else:
                    reported_ad = None
                    reported_user = random.choice(users)
                    # Ensure not reporting themselves
                    while reported_user == reporter:
                        reported_user = random.choice(users)

                # Use Arabic descriptions or generate fake ones
                if random.random() > 0.5:
                    description = random.choice(arabic_descriptions)
                else:
                    description = fake.paragraph(nb_sentences=3)

                # Weighted status: 40% pending, 30% reviewing, 20% resolved, 10% rejected
                status = random.choices(
                    statuses,
                    weights=[40, 30, 20, 10],
                    k=1,
                )[0]

                report = AdReport.objects.create(
                    reporter=reporter,
                    report_type=report_type,
                    status=status,
                    reported_ad=reported_ad,
                    reported_user=reported_user,
                    description=description,
                )

                # Add admin notes for resolved/rejected reports
                if status in ["resolved", "rejected"]:
                    admin_users = User.objects.filter(is_staff=True)
                    if admin_users.exists():
                        report.reviewed_by = random.choice(list(admin_users))
                        report.admin_notes = fake.sentence(nb_words=8)
                        report.resolved_at = timezone.now() - timedelta(
                            days=random.randint(1, 30)
                        )
                        report.save()

                # Randomize created_at
                days_ago = random.randint(1, 90)
                report.created_at = timezone.now() - timedelta(days=days_ago)
                report.save(update_fields=["created_at"])

                created += 1
                # Encode title safely for Windows console
                if reported_ad:
                    try:
                        title_preview = reported_ad.title[:25]
                        title_preview.encode('cp1252')
                        target = f"Ad: {title_preview}..."
                    except (UnicodeEncodeError, AttributeError):
                        target = "Ad: [Arabic Title]"
                else:
                    target = f"User: {reported_user.username}"

                self.stdout.write(
                    f"  [OK] Created report #{i+1}: {target} ({report_type})"
                )

            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"  [SKIP] Skipping report #{i+1}: {str(e)}"
                    )
                )

        return created

    def _create_user_packages(self, fake, users, packages, count):
        """Create dummy user packages."""
        created = 0
        self.stdout.write(f"\nCreating {count} user packages...")

        for i in range(count):
            try:
                user = random.choice(users)
                package = random.choice(packages)

                # Calculate dates
                purchase_date = timezone.now() - timedelta(
                    days=random.randint(1, 365)
                )
                expiry_date = purchase_date + timedelta(
                    days=package.duration_days
                )

                # Calculate ads used and remaining
                total_ads = package.ad_count
                ads_used = random.randint(0, total_ads)
                ads_remaining = total_ads - ads_used

                # Create payment record (optional - 80% with payment)
                payment = None
                if random.random() > 0.2:
                    payment = Payment.objects.create(
                        user=user,
                        amount=package.price,
                        status="completed",
                        provider="paymob",
                        provider_transaction_id=fake.uuid4(),
                        completed_at=purchase_date,
                    )
                    payment.created_at = purchase_date
                    payment.save(update_fields=["created_at"])

                user_package = UserPackage.objects.create(
                    user=user,
                    package=package,
                    payment=payment,
                    purchase_date=purchase_date,
                    expiry_date=expiry_date,
                    ads_remaining=ads_remaining,
                    ads_used=ads_used,
                )

                # Update created date
                user_package.purchase_date = purchase_date
                user_package.save(update_fields=["purchase_date"])

                status = "Active" if user_package.is_active() else "Expired"
                created += 1
                # Encode package name safely for Windows console
                try:
                    package_name = package.name
                    package_name.encode('cp1252')
                except (UnicodeEncodeError, AttributeError):
                    package_name = "Package"
                self.stdout.write(
                    f"  [OK] Created package #{i+1}: {user.username} - {package_name} ({status})"
                )

            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"  [SKIP] Skipping package #{i+1}: {str(e)}"
                    )
                )

        return created

    def _create_reservations(self, fake, users, ads, count):
        """Create dummy ad reservations."""
        created = 0
        self.stdout.write(f"\nCreating {count} ad reservations...")

        # Sample Arabic notes
        arabic_notes = [
            "أرجو التواصل قبل التوصيل",
            "أفضل التوصيل في المساء",
            "يرجى التأكد من حالة المنتج",
            "متى يمكنني الاستلام؟",
            "هل المنتج متوفر للفحص؟",
            "أود رؤية المنتج قبل الدفع الكامل",
            "التوصيل إلى المنزل من فضلك",
            "متى يمكنني دفع المبلغ المتبقي؟",
            "هل يمكن التفاوض على السعر؟",
            "أريد التأكد من المواصفات",
        ]

        # Sample Arabic addresses
        arabic_addresses = [
            "الرياض، حي النخيل، شارع الملك فهد",
            "جدة، حي الحمراء، طريق الكورنيش",
            "الدمام، حي الفيصلية، شارع الأمير محمد",
            "مكة المكرمة، حي العزيزية، شارع النور",
            "المدينة المنورة، حي العيون، طريق السلام",
            "الخبر، حي الثقبة، طريق الخليج",
            "الطائف، حي السلامة، شارع الحرمين",
            "القصيم، بريدة، حي الصفراء",
            "أبها، حي المنسك، شارع الملك عبدالعزيز",
            "تبوك، حي السليمانية، طريق المدينة",
        ]

        statuses = [choice[0] for choice in AdReservation.ReservationStatus.choices]

        for i in range(count):
            try:
                user = random.choice(users)
                ad = random.choice(ads)

                # Generate realistic amounts
                # Assume ad has a price field, if not we'll generate one
                try:
                    base_price = float(ad.price) if hasattr(ad, 'price') and ad.price else random.uniform(100, 10000)
                except (ValueError, TypeError, AttributeError):
                    base_price = random.uniform(100, 10000)

                full_amount = round(base_price, 2)

                # Reservation amount is typically 10-50% of full amount
                reservation_percentage = random.uniform(0.1, 0.5)
                reservation_amount = round(full_amount * reservation_percentage, 2)

                # Delivery fee between 0-100 SAR
                delivery_fee = round(random.uniform(0, 100), 2)

                # Status distribution: 30% pending, 40% confirmed, 15% completed, 10% cancelled, 5% refunded
                status = random.choices(
                    statuses,
                    weights=[30, 40, 15, 10, 5],
                    k=1
                )[0]

                # Notes (50% have notes)
                if random.random() > 0.5:
                    notes = random.choice(arabic_notes)
                else:
                    notes = ""

                # Delivery address (70% have delivery addresses)
                if random.random() > 0.3:
                    delivery_address = random.choice(arabic_addresses)
                else:
                    delivery_address = ""

                # Calculate created and expiry dates
                days_ago = random.randint(1, 60)
                created_at = timezone.now() - timedelta(days=days_ago)

                # Expiry is 48 hours from creation for pending/confirmed, or in the past for completed/cancelled
                if status in ['pending', 'confirmed']:
                    expires_at = created_at + timedelta(hours=48)
                else:
                    # For completed/cancelled, expiry is in the past
                    expires_at = created_at + timedelta(hours=random.randint(1, 47))

                reservation = AdReservation.objects.create(
                    ad=ad,
                    user=user,
                    reservation_amount=reservation_amount,
                    full_amount=full_amount,
                    status=status,
                    notes=notes,
                    delivery_address=delivery_address,
                    delivery_fee=delivery_fee,
                    expires_at=expires_at,
                )

                # Update created_at
                reservation.created_at = created_at
                reservation.save(update_fields=["created_at"])

                created += 1
                # Encode title safely for Windows console
                try:
                    title_preview = ad.title[:25]
                    title_preview.encode('cp1252')
                except (UnicodeEncodeError, AttributeError):
                    title_preview = "Ad"

                amount_info = f"{reservation_amount:.2f}/{full_amount:.2f} SAR"
                self.stdout.write(
                    f"  [OK] Created reservation #{i+1}: {user.username} -> {title_preview}... ({status}, {amount_info})"
                )

            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"  [SKIP] Skipping reservation #{i+1}: {str(e)}"
                    )
                )

        return created
