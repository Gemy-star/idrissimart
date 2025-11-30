"""
Payment Services for PayPal and Paymob integration
This module coordinates payment providers using the new service modules
"""

import logging
from decimal import Decimal
from constance import config
from django.utils.translation import gettext_lazy as _

# Import new service modules
from .services.paypal_service import PayPalService
from .services.paymob_service import PaymobService

logger = logging.getLogger(__name__)


class PaymentService:
    """Main payment service that coordinates different payment providers"""

    def __init__(self):
        self.paypal = PayPalService()
        self.paymob = PaymobService()

    def create_payment(
        self, provider, amount, currency, description, user_data=None, **kwargs
    ):
        """Create payment with specified provider"""
        if provider == "paypal":
            return self.paypal.process_payment(
                amount=amount,
                currency=currency,
                description=description,
                return_url=kwargs.get("return_url"),
                cancel_url=kwargs.get("cancel_url"),
            )
        elif provider == "paymob":
            return self.paymob.process_payment(
                amount=amount, currency=currency, billing_data=user_data or {}
            )
        elif provider in ["mastercard", "visa"]:
            # Redirect to Paymob for card payments
            integration_id = config.PAYMOB_INTEGRATION_ID
            return self.paymob.process_payment(
                amount=amount,
                currency="EGP",
                billing_data=user_data or {},
                integration_id=integration_id,
            )
        else:
            return False, _("مزود الدفع غير مدعوم")

    def get_supported_providers(self):
        """Get list of supported payment providers based on django-constance configuration"""
        providers = []

        # Check PayPal configuration from constance
        if PayPalService.is_enabled():
            providers.append(
                {
                    "id": "paypal",
                    "name": "PayPal",
                    "currencies": ["USD", "EUR", "SAR"],
                    "icon": "fab fa-cc-paypal",
                }
            )

        # Check Paymob configuration from constance
        if PaymobService.is_enabled():
            providers.append(
                {
                    "id": "paymob",
                    "name": "Paymob",
                    "currencies": ["EGP"],
                    "icon": "fas fa-credit-card",
                }
            )

        # Always show Mastercard option (redirects to Paymob)
        providers.append(
            {
                "id": "mastercard",
                "name": "Mastercard",
                "currencies": ["EGP", "SAR"],
                "icon": "fab fa-cc-mastercard",
            }
        )

        # Always show Visa option (redirects to Paymob)
        providers.append(
            {
                "id": "visa",
                "name": "Visa",
                "currencies": ["EGP", "SAR", "USD"],
                "icon": "fab fa-cc-visa",
            }
        )

        return providers
