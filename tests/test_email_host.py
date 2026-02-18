#!/usr/bin/env python
"""
Test email templates from host machine (outside Docker)
Uses localhost:2525 instead of smtp4dev:25
Run with: python test_email_host.py
"""

import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings.local")

# Override email settings for host testing
os.environ["EMAIL_HOST"] = "localhost"
os.environ["EMAIL_PORT"] = "2525"

django.setup()

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

# Update settings
settings.EMAIL_HOST = "localhost"
settings.EMAIL_PORT = 2525


def test_welcome_email():
    """Test welcome email template"""
    print("\n📧 Sending welcome email...")

    context = {
        "site_name": "إدريسي مارت",
        "user_name": "أحمد محمد",
        "site_url": "http://localhost:8000",
    }

    html_content = render_to_string("emails/welcome.html", context)

    email = EmailMultiAlternatives(
        subject="مرحباً بك في إدريسي مارت 🎉",
        body="مرحباً بك في إدريسي مارت",
        from_email="noreply@idrissimart.local",
        to=["user@example.com"],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()

    print("✅ Welcome email sent successfully!")


def test_otp_email():
    """Test OTP verification email template"""
    print("\n📧 Sending OTP verification email...")

    context = {
        "site_name": "إدريسي مارت",
        "user_name": "فاطمة علي",
        "otp_code": "742839",
        "expiry_minutes": 10,
    }

    html_content = render_to_string("emails/otp_verification.html", context)

    email = EmailMultiAlternatives(
        subject="رمز التحقق من الحساب 🔐",
        body="رمز التحقق الخاص بك هو: 742839",
        from_email="noreply@idrissimart.local",
        to=["user@example.com"],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()

    print("✅ OTP email sent successfully!")


def test_password_reset_email():
    """Test password reset email template"""
    print("\n📧 Sending password reset email...")

    context = {
        "site_name": "إدريسي مارت",
        "user_name": "خالد السعيد",
        "reset_link": "http://localhost:8000/reset/Mg/abc123-def456-ghi789/",
        "site_url": "http://localhost:8000",
    }

    html_content = render_to_string("emails/password_reset.html", context)

    email = EmailMultiAlternatives(
        subject="إعادة تعيين كلمة المرور 🔑",
        body="اضغط على الرابط لإعادة تعيين كلمة المرور",
        from_email="noreply@idrissimart.local",
        to=["user@example.com"],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()

    print("✅ Password reset email sent successfully!")


def test_ad_approved_email():
    """Test ad approval email template"""
    print("\n📧 Sending ad approval email...")

    context = {
        "site_name": "إدريسي مارت",
        "user_name": "سارة أحمد",
        "ad_title": "آيفون 14 برو ماكس - حالة ممتازة",
        "ad_url": "http://localhost:8000/ad/iphone-14-pro-max-excellent-condition",
        "site_url": "http://localhost:8000",
    }

    html_content = render_to_string("emails/ad_approved.html", context)

    email = EmailMultiAlternatives(
        subject="تمت الموافقة على إعلانك ✓",
        body="تمت الموافقة على إعلانك وهو الآن مُفعّل",
        from_email="noreply@idrissimart.local",
        to=["user@example.com"],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()

    print("✅ Ad approval email sent successfully!")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Testing Email Templates (Host Machine)")
    print("=" * 60)
    print("\n📍 Configuration:")
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
    print("\n📍 Make sure smtp4dev is running:")
    print("   docker compose up -d smtp4dev")
    print("\n🌐 View emails at: http://localhost:3100")
    print("=" * 60)

    try:
        # Test all email templates
        test_welcome_email()
        test_otp_email()
        test_password_reset_email()
        test_ad_approved_email()

        print("\n" + "=" * 60)
        print("✅ All email templates sent successfully!")
        print("🌐 Check your emails at: http://localhost:3100")
        print("=" * 60)
        print("\n📋 Templates tested:")
        print("   1. ✓ Welcome Email (emails/welcome.html)")
        print("   2. ✓ OTP Verification (emails/otp_verification.html)")
        print("   3. ✓ Password Reset (emails/password_reset.html)")
        print("   4. ✓ Ad Approved (emails/ad_approved.html)")
        print("\n🎨 All templates use Idrissimart brand colors:")
        print("   • Primary: #4b315e (Purple)")
        print("   • Secondary: #ff6001 (Orange)")
        print("   • Font: Cairo, sans-serif")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check if smtp4dev is running:")
        print("      docker compose ps smtp4dev")
        print("   2. Check if port 2525 is available:")
        print("      sudo netstat -tulpn | grep 2525")
        print("   3. Check logs:")
        print("      docker compose logs smtp4dev")
        print("   4. Make sure templates exist in templates/emails/")
        print("=" * 60)
