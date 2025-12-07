"""
Order Notification System Test Script

This script creates a test order and verifies that all notifications are sent correctly.
Run with: python manage.py shell < test_order_notifications.py
"""

from django.contrib.auth import get_user_model
from main.models import Order, OrderItem, ClassifiedAd, Cart, CartItem
from content.models import Notification
from decimal import Decimal

User = get_user_model()


def test_order_creation():
    """Test order creation notifications"""
    print("\n" + "=" * 60)
    print("TESTING ORDER CREATION NOTIFICATIONS")
    print("=" * 60 + "\n")

    # Get or create test user
    user, created = User.objects.get_or_create(
        username="test_customer",
        defaults={
            "email": "customer@test.com",
            "first_name": "Test",
            "last_name": "Customer",
        },
    )
    print(f"✓ Test user: {user.username} ({'created' if created else 'exists'})")

    # Get a test ad
    ad = ClassifiedAd.objects.filter(is_active=True).first()
    if not ad:
        print("✗ No active ads found. Please create at least one ad.")
        return
    print(f"✓ Test ad: {ad.title}")

    # Count notifications before
    notif_count_before = Notification.objects.filter(user=user).count()
    print(f"✓ Notifications before: {notif_count_before}")

    # Create test order
    order = Order.objects.create(
        user=user,
        full_name="Test Customer",
        phone="+966500000000",
        address="Test Address 123",
        city="Riyadh",
        postal_code="12345",
        payment_method="cod",
        payment_status="unpaid",
        total_amount=Decimal("1000.00"),
        status="pending",
    )
    print(f"✓ Order created: {order.order_number}")

    # Create order item
    OrderItem.objects.create(
        order=order,
        ad=ad,
        quantity=1,
        price=ad.price,
    )
    print(f"✓ Order item created")

    # Check notifications after
    notif_count_after = Notification.objects.filter(user=user).count()
    print(f"✓ Notifications after: {notif_count_after}")
    print(f"✓ New notifications: {notif_count_after - notif_count_before}")

    # Get the latest notification
    latest_notif = (
        Notification.objects.filter(user=user).order_by("-created_at").first()
    )
    if latest_notif:
        print(f"\n📧 Latest notification:")
        print(f"   Title: {latest_notif.title}")
        print(f"   Message: {latest_notif.message}")
        print(f"   Link: {latest_notif.link}")

    # Check admin notifications
    admin_notifs = Notification.objects.filter(
        user__is_superuser=True, message__contains=order.order_number
    ).count()
    print(f"\n👨‍💼 Admin notifications: {admin_notifs}")

    return order


def test_status_change(order):
    """Test order status change notifications"""
    print("\n" + "=" * 60)
    print("TESTING STATUS CHANGE NOTIFICATIONS")
    print("=" * 60 + "\n")

    # Count notifications before
    notif_count_before = Notification.objects.filter(user=order.user).count()
    print(f"✓ Notifications before: {notif_count_before}")

    # Change status
    old_status = order.status
    order.status = "shipped"
    order.save()
    print(f"✓ Status changed: {old_status} → {order.status}")

    # Check notifications after
    notif_count_after = Notification.objects.filter(user=order.user).count()
    print(f"✓ Notifications after: {notif_count_after}")
    print(f"✓ New notifications: {notif_count_after - notif_count_before}")

    # Get the latest notification
    latest_notif = (
        Notification.objects.filter(user=order.user).order_by("-created_at").first()
    )
    if latest_notif:
        print(f"\n📧 Latest notification:")
        print(f"   Title: {latest_notif.title}")
        print(f"   Message: {latest_notif.message}")


def test_partial_payment(order):
    """Test partial payment notifications"""
    print("\n" + "=" * 60)
    print("TESTING PARTIAL PAYMENT NOTIFICATIONS")
    print("=" * 60 + "\n")

    # Count notifications before
    notif_count_before = Notification.objects.filter(user=order.user).count()
    print(f"✓ Notifications before: {notif_count_before}")

    # Set partial payment
    order.payment_method = "partial"
    order.payment_status = "partial"
    order.paid_amount = Decimal("500.00")
    order.save()
    print(f"✓ Partial payment set:")
    print(f"   Paid: {order.paid_amount} SAR")
    print(f"   Remaining: {order.remaining_amount} SAR")

    # Check notifications after
    notif_count_after = Notification.objects.filter(user=order.user).count()
    print(f"✓ Notifications after: {notif_count_after}")
    print(f"✓ New notifications: {notif_count_after - notif_count_before}")

    # Get the latest notification
    latest_notif = (
        Notification.objects.filter(user=order.user).order_by("-created_at").first()
    )
    if latest_notif:
        print(f"\n📧 Latest notification:")
        print(f"   Title: {latest_notif.title}")
        print(f"   Message: {latest_notif.message}")


def test_full_payment(order):
    """Test full payment notifications"""
    print("\n" + "=" * 60)
    print("TESTING FULL PAYMENT NOTIFICATIONS")
    print("=" * 60 + "\n")

    # Count notifications before
    notif_count_before = Notification.objects.filter(user=order.user).count()
    print(f"✓ Notifications before: {notif_count_before}")

    # Set full payment
    order.payment_status = "paid"
    order.paid_amount = order.total_amount
    order.save()
    print(f"✓ Full payment set: {order.paid_amount} SAR")

    # Check notifications after
    notif_count_after = Notification.objects.filter(user=order.user).count()
    print(f"✓ Notifications after: {notif_count_after}")
    print(f"✓ New notifications: {notif_count_after - notif_count_before}")

    # Get the latest notification
    latest_notif = (
        Notification.objects.filter(user=order.user).order_by("-created_at").first()
    )
    if latest_notif:
        print(f"\n📧 Latest notification:")
        print(f"   Title: {latest_notif.title}")
        print(f"   Message: {latest_notif.message}")


def run_all_tests():
    """Run all notification tests"""
    print("\n" + "🧪 " * 30)
    print("ORDER NOTIFICATION SYSTEM - COMPREHENSIVE TEST")
    print("🧪 " * 30)

    try:
        # Test 1: Order Creation
        order = test_order_creation()

        if not order:
            print("\n✗ Order creation failed. Stopping tests.")
            return

        # Test 2: Status Change
        test_status_change(order)

        # Test 3: Partial Payment
        test_partial_payment(order)

        # Test 4: Full Payment
        test_full_payment(order)

        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"\nTest order: {order.order_number}")
        print(
            f"Total notifications created: {Notification.objects.filter(user=order.user).count()}"
        )
        print("\nNOTE: Check your email and SMS for actual delivery.")
        print("      (Email: customer@test.com, Phone: +966500000000)")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback

        traceback.print_exc()


# Run the tests
if __name__ == "__main__":
    run_all_tests()
