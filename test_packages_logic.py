import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings")
django.setup()

from content.site_config import SiteConfiguration
from django.contrib.auth import get_user_model
from main.models import AdPackage

User = get_user_model()
user = User.objects.first()
sc = SiteConfiguration.get_solo()

print("=== Site Configuration ===")
print(f"Require email verification: {sc.require_email_verification}")
print(f"Require phone verification: {sc.require_phone_verification}")

print("\n=== User Status ===")
print(f"User: {user.username if user else 'No users'}")
if user:
    print(f"Email verified: {getattr(user, 'is_email_verified', False)}")
    print(f"Phone verified: {getattr(user, 'is_phone_verified', False)}")

print("\n=== Logic Simulation (Authenticated User) ===")
email_verified = True
phone_verified = True

if sc.require_email_verification:
    email_verified = getattr(user, "is_email_verified", False) if user else False

if sc.require_phone_verification:
    phone_verified = getattr(user, "is_phone_verified", False) if user else False

print(f"Email verified (after check): {email_verified}")
print(f"Phone verified (after check): {phone_verified}")

user_fully_verified = email_verified and phone_verified
show_all_packages = user_fully_verified

print(f"User fully verified: {user_fully_verified}")
print(f"Show all packages: {show_all_packages}")

show_email_warning = sc.require_email_verification and not email_verified
show_phone_warning = sc.require_phone_verification and not phone_verified

print(f"Show email warning: {show_email_warning}")
print(f"Show phone warning: {show_phone_warning}")

print("\n=== Packages Query ===")
if show_all_packages:
    packages = AdPackage.objects.filter(category__isnull=True, is_active=True)
else:
    packages = AdPackage.objects.filter(category__isnull=True, is_active=True, price=0)

print(f"Packages count: {packages.count()}")
for pkg in packages:
    print(f"  - {pkg.name}: {pkg.price} SAR")
