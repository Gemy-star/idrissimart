#!/usr/bin/env python
"""
Test Email Templates - Comprehensive Email Integration Testing
Tests all email templates created for signal-triggered notifications

Usage:
    docker exec -it idrissimart_web python test_signal_emails.py

    Or from host machine:
    python test_signal_emails.py
"""

import os
import sys
import django
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings.local")
django.setup()

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailTester:
    """Test email templates with smtp4dev"""

    def __init__(self):
        # Check if running in container or on host
        try:
            # Try container hostname first
            self.smtp_host = "smtp4dev"
            self.smtp_port = 25
            # Test connection
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=2) as server:
                server.noop()
            print("✓ Connected to smtp4dev container")
        except:
            # Fall back to host machine
            self.smtp_host = "localhost"
            self.smtp_port = 2525
            try:
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=2) as server:
                    server.noop()
                print("✓ Connected to smtp4dev on host machine")
            except Exception as e:
                print(f"❌ Cannot connect to smtp4dev: {e}")
                print("Please start smtp4dev: docker compose up smtp4dev")
                sys.exit(1)

        self.from_email = "noreply@idrissimart.local"
        self.to_email = "test@example.com"
        self.web_ui_url = "http://localhost:3100"

    def send_html_email(self, subject, template_name, context):
        """Send HTML email using template"""
        try:
            # Render template
            html_content = render_to_string(template_name, context)

            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = self.to_email

            # Add HTML part
            html_part = MIMEText(html_content, "html", "utf-8")
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.send_message(msg)

            print(f"  ✓ Sent: {subject}")
            return True

        except Exception as e:
            print(f"  ❌ Failed to send {subject}: {e}")
            return False

    def test_welcome_email(self):
        """Test welcome email template"""
        print("\n1. Testing Welcome Email...")
        context = {
            "site_name": "إدريسي مارت",
            "user_name": "أحمد محمد",
            "site_url": "http://localhost:8000",
        }
        return self.send_html_email(
            subject="مرحباً بك في إدريسي مارت",
            template_name="emails/welcome.html",
            context=context,
        )

    def test_otp_email(self):
        """Test OTP verification email template"""
        print("\n2. Testing OTP Verification Email...")
        context = {
            "site_name": "إدريسي مارت",
            "user_name": "أحمد محمد",
            "otp_code": "123456",
            "expiry_minutes": 10,
        }
        return self.send_html_email(
            subject="إدريسي مارت - رمز التحقق",
            template_name="emails/otp_verification.html",
            context=context,
        )

    def test_password_reset_email(self):
        """Test password reset email template"""
        print("\n3. Testing Password Reset Email...")
        context = {
            "site_name": "إدريسي مارت",
            "user_name": "أحمد محمد",
            "reset_link": "http://localhost:8000/accounts/password-reset/confirm/abc123/",
        }
        return self.send_html_email(
            subject="إدريسي مارت - إعادة تعيين كلمة المرور",
            template_name="emails/password_reset.html",
            context=context,
        )

    def test_ad_approved_email(self):
        """Test ad approval email template"""
        print("\n4. Testing Ad Approval Email...")
        context = {
            "site_name": "إدريسي مارت",
            "user_name": "أحمد محمد",
            "ad_title": "شقة للإيجار في مدينة نصر",
            "ad_url": "http://localhost:8000/ads/123/",
        }
        return self.send_html_email(
            subject="تمت الموافقة على إعلانك - شقة للإيجار في مدينة نصر",
            template_name="emails/ad_approved.html",
            context=context,
        )

    def test_order_created_email(self):
        """Test order creation email template"""
        print("\n5. Testing Order Created Email...")

        # Mock order object
        class MockOrder:
            order_number = "ORD-2024-001"
            total_amount = 1500.00
            created_at = timezone.now()
            id = 123
            full_name = "أحمد محمد"
            email = "test@example.com"
            phone = "+20 100 123 4567"
            address = "123 شارع النهضة"
            city = "القاهرة"
            payment_status = "pending"

            def items_list(self):
                return [
                    {"ad_title": "هاتف آيفون 15 برو", "quantity": 1, "price": 800.00},
                    {"ad_title": "سماعات لاسلكية", "quantity": 2, "price": 350.00},
                ]

        class MockUser:
            username = "ahmed"
            email = "test@example.com"

            def get_full_name(self):
                return "أحمد محمد"

        order = MockOrder()
        user = MockUser()

        context = {
            "order": order,
            "user": user,
            "items": [
                {
                    "ad": {"title": "هاتف آيفون 15 برو"},
                    "quantity": 1,
                    "price": 800.00,
                },
                {
                    "ad": {"title": "سماعات لاسلكية"},
                    "quantity": 2,
                    "price": 350.00,
                },
            ],
            "site_url": "http://localhost:8000",
        }
        return self.send_html_email(
            subject=f"تأكيد الطلب - {order.order_number}",
            template_name="emails/order_created.html",
            context=context,
        )

    def test_package_activated_email(self):
        """Test package activation email template"""
        print("\n6. Testing Package Activation Email...")

        # Mock package and user_package objects
        class MockPackage:
            name = "باقة الناشر الفضية"
            ad_count = 50
            duration_days = 30
            price = 500.00

        class MockUserPackage:
            expiry_date = timezone.now() + timedelta(days=30)

        class MockUser:
            username = "publisher1"
            email = "test@example.com"

            def get_full_name(self):
                return "محمد علي"

        package = MockPackage()
        user_package = MockUserPackage()
        user = MockUser()

        context = {
            "user": user,
            "package": package,
            "user_package": user_package,
            "payment_amount": 500.00,
            "site_name": "إدريسي مارت",
            "site_url": "http://localhost:8000",
        }
        return self.send_html_email(
            subject="تم تفعيل باقتك - Package Activated",
            template_name="emails/package_activated.html",
            context=context,
        )

    def test_order_status_update_email(self, status="shipped"):
        """Test order status update email template"""
        print(f"\n7. Testing Order Status Update Email (Status: {status})...")

        # Mock order object
        class MockOrder:
            order_number = "ORD-2024-001"
            total_amount = 1500.00
            created_at = timezone.now()
            id = 123
            full_name = "أحمد محمد"
            email = "test@example.com"
            phone = "+20 100 123 4567"
            address = "123 شارع النهضة"
            city = "القاهرة"
            payment_status = "paid"
            tracking_number = "TRACK123456"
            shipping_carrier = "DHL"

            def __init__(self, status):
                self.status = status

        class MockUser:
            email = "test@example.com"

            def get_full_name(self):
                return "أحمد محمد"

        order = MockOrder(status)
        order.user = MockUser()

        context = {
            "order": order,
            "currency": "ج.م",
            "site_name": "إدريسي مارت",
            "site_url": "http://localhost:8000",
        }

        status_subjects = {
            "processing": "طلبك قيد المعالجة",
            "shipped": "تم شحن طلبك",
            "delivered": "تم تسليم طلبك بنجاح",
            "cancelled": "تم إلغاء طلبك",
            "refunded": "تم استرداد مبلغ طلبك",
        }

        subject = status_subjects.get(status, "تحديث حالة الطلب")

        return self.send_html_email(
            subject=f"{subject} - {order.order_number}",
            template_name="emails/order_status_update.html",
            context=context,
        )

    def test_saved_search_notification_email(self):
        """Test saved search notification email template"""
        print("\n8. Testing Saved Search Notification Email...")

        context = {
            "site_name": "إدريسي مارت",
            "user_name": "أحمد محمد",
            "search_name": "شقق للإيجار في مدينة نصر",
            "ads": [
                {
                    "title": "شقة 3 غرف للإيجار",
                    "price": 3000,
                    "location": "مدينة نصر",
                    "get_absolute_url": lambda: "http://localhost:8000/ads/1/",
                },
                {
                    "title": "شقة دوبلكس فاخرة",
                    "price": 5000,
                    "location": "مدينة نصر",
                    "get_absolute_url": lambda: "http://localhost:8000/ads/2/",
                },
            ],
            "search_url": "http://localhost:8000/saved-searches/1/",
        }
        return self.send_html_email(
            subject="إعلانات جديدة تطابق بحثك - شقق للإيجار في مدينة نصر",
            template_name="emails/saved_search_notification.html",
            context=context,
        )

    def run_all_tests(self):
        """Run all email template tests"""
        print("=" * 60)
        print("Email Templates Test Suite")
        print("=" * 60)
        print(f"\nSMTP Server: {self.smtp_host}:{self.smtp_port}")
        print(f"Web UI: {self.web_ui_url}")
        print("=" * 60)

        results = []

        # Run all tests
        results.append(("Welcome Email", self.test_welcome_email()))
        results.append(("OTP Email", self.test_otp_email()))
        results.append(("Password Reset", self.test_password_reset_email()))
        results.append(("Ad Approved", self.test_ad_approved_email()))
        results.append(("Order Created", self.test_order_created_email()))
        results.append(("Package Activated", self.test_package_activated_email()))

        # Test all order status variants
        for status in ["processing", "shipped", "delivered", "cancelled", "refunded"]:
            results.append(
                (
                    f"Order Status: {status}",
                    self.test_order_status_update_email(status),
                )
            )

        results.append(
            ("Saved Search", self.test_saved_search_notification_email())
        )

        # Print summary
        print("\n" + "=" * 60)
        print("Test Results Summary")
        print("=" * 60)

        successful = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")

        print("\n" + "=" * 60)
        print(f"Total: {successful}/{total} tests passed")
        print("=" * 60)

        if successful == total:
            print("\n🎉 All tests passed successfully!")
        else:
            print(f"\n⚠️  {total - successful} test(s) failed!")

        print(f"\n📧 Check your emails at: {self.web_ui_url}")
        print("=" * 60)

        return successful == total


if __name__ == "__main__":
    tester = EmailTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
