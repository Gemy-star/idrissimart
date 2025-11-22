import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings")
django.setup()

from main.payment_services import PaymentService
from constance import config

print("=" * 60)
print("PAYMENT PROVIDERS CHECK")
print("=" * 60)

# Check Constance settings
print("\n1. Constance Configuration:")
print(f"   PAYMOB_API_KEY: {'SET' if config.PAYMOB_API_KEY else 'NOT SET'}")
print(
    f"   PAYMOB_INTEGRATION_ID: {config.PAYMOB_INTEGRATION_ID if config.PAYMOB_INTEGRATION_ID else 'NOT SET'}"
)
print(
    f"   PAYMOB_MASTERCARD_INTEGRATION_ID: {config.PAYMOB_MASTERCARD_INTEGRATION_ID if config.PAYMOB_MASTERCARD_INTEGRATION_ID else 'NOT SET'}"
)
print(
    f"   PAYMOB_VISA_INTEGRATION_ID: {config.PAYMOB_VISA_INTEGRATION_ID if config.PAYMOB_VISA_INTEGRATION_ID else 'NOT SET'}"
)
print(f"   PAYPAL_CLIENT_ID: {'SET' if config.PAYPAL_CLIENT_ID else 'NOT SET'}")

# Get supported providers
ps = PaymentService()
providers = ps.get_supported_providers()

print(f"\n2. Supported Providers ({len(providers)} total):")
for p in providers:
    print(f"   - {p['id']}: {p['name']}")
    print(f"     Icon: {p['icon']}")
    print(f"     Currencies: {', '.join(p['currencies'])}")
    print()

print("=" * 60)
