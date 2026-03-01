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
        """
        Create payment with specified provider.

        Returns:
            (True, {"approval_url": ..., "paypal_order_id": ...})  for PayPal
            (True, {"iframe_url": ...})                             for Paymob/visa/mastercard
            (False, "error message string")                        on failure
        """
        import uuid
        order_ref = kwargs.get("order_ref") or uuid.uuid4().hex[:12].upper()

        if provider == "paypal":
            success, order_data, error = PayPalService.create_order(
                amount=amount,
                currency=currency,
                order_id=order_ref,
                description=description,
                return_url=kwargs.get("return_url"),
                cancel_url=kwargs.get("cancel_url"),
            )
            if not success:
                return False, error or _("فشل إنشاء طلب PayPal")
            approval_url = PayPalService.get_approval_url(order_data)
            if not approval_url:
                return False, _("تعذّر الحصول على رابط PayPal")
            return True, {
                "approval_url": approval_url,
                "paypal_order_id": order_data.get("id"),
            }

        elif provider in ["paymob", "mastercard", "visa"]:
            integration_id = None
            if provider in ["mastercard", "visa"]:
                integration_id = config.PAYMOB_INTEGRATION_ID
            success, payment_url, error, paymob_order_id = PaymobService.process_payment(
                amount=amount,
                order_id=order_ref,
                billing_data=user_data or {},
                integration_id=integration_id,
            )
            if not success:
                return False, error or _("فشل إنشاء طلب Paymob")
            return True, {"iframe_url": payment_url, "paymob_order_id": paymob_order_id}

        else:
            return False, _("مزود الدفع غير مدعوم")

    def get_supported_providers(self):
        """Get list of supported payment providers based on django-constance and site configuration"""
        providers = []

        # Check SiteConfiguration for allow_online_payment
        try:
            from content.models import SiteConfiguration

            site_config = SiteConfiguration.get_solo()
            if not site_config.allow_online_payment:
                return providers
        except Exception:
            pass  # If SiteConfiguration is not available, proceed

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

            # Only show Mastercard and Visa if Paymob is enabled
            providers.append(
                {
                    "id": "mastercard",
                    "name": "Mastercard",
                    "currencies": ["EGP", "SAR"],
                    "icon": "fab fa-cc-mastercard",
                }
            )

            providers.append(
                {
                    "id": "visa",
                    "name": "Visa",
                    "currencies": ["EGP", "SAR", "USD"],
                    "icon": "fab fa-cc-visa",
                }
            )

        return providers
