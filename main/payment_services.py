"""
Payment Services for PayPal and Paymob integration
"""

import json
import requests
import logging
from decimal import Decimal
from constance import config
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PayPalService:
    """Service for handling PayPal payments"""

    def __init__(self):
        # Get PayPal configuration from django-constance
        self.client_id = getattr(config, "PAYPAL_CLIENT_ID", "")
        self.client_secret = getattr(config, "PAYPAL_CLIENT_SECRET", "")
        self.mode = getattr(config, "PAYPAL_MODE", "sandbox")  # sandbox or live

        if not self.client_id or not self.client_secret:
            logger.warning("PayPal credentials not configured in django-constance")

        if self.mode == "sandbox":
            self.base_url = "https://api.sandbox.paypal.com"
        else:
            self.base_url = "https://api.paypal.com"

        self.access_token = None
        self.token_expires = None

    def get_access_token(self):
        """Get PayPal access token"""
        if not self.client_id or not self.client_secret:
            logger.error("PayPal credentials not configured")
            return None

        if (
            self.access_token
            and self.token_expires
            and timezone.now() < self.token_expires
        ):
            return self.access_token

        url = f"{self.base_url}/v1/oauth2/token"
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en_US",
        }
        data = "grant_type=client_credentials"

        try:
            response = requests.post(
                url,
                headers=headers,
                data=data,
                auth=(self.client_id, self.client_secret),
            )
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires = timezone.now() + timedelta(seconds=expires_in - 60)

            return self.access_token

        except requests.exceptions.RequestException as e:
            logger.error(f"PayPal token error: {str(e)}")
            return None

    def create_payment(
        self,
        amount,
        currency="USD",
        description="Payment",
        return_url=None,
        cancel_url=None,
    ):
        """Create a PayPal payment"""
        access_token = self.get_access_token()
        if not access_token:
            return False, _("فشل في الاتصال بـ PayPal")

        url = f"{self.base_url}/v1/payments/payment"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

        payment_data = {
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "transactions": [
                {
                    "amount": {"total": str(amount), "currency": currency},
                    "description": description,
                }
            ],
            "redirect_urls": {
                "return_url": return_url
                or f"{config.SITE_URL}/payment/paypal/success/",
                "cancel_url": cancel_url or f"{config.SITE_URL}/payment/paypal/cancel/",
            },
        }

        try:
            response = requests.post(url, headers=headers, json=payment_data)
            response.raise_for_status()

            payment_response = response.json()

            # Extract approval URL
            approval_url = None
            for link in payment_response.get("links", []):
                if link.get("rel") == "approval_url":
                    approval_url = link.get("href")
                    break

            return True, {
                "payment_id": payment_response.get("id"),
                "approval_url": approval_url,
                "status": payment_response.get("state"),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"PayPal payment creation error: {str(e)}")
            return False, _("فشل في إنشاء عملية الدفع")

    def execute_payment(self, payment_id, payer_id):
        """Execute a PayPal payment after approval"""
        access_token = self.get_access_token()
        if not access_token:
            return False, _("فشل في الاتصال بـ PayPal")

        url = f"{self.base_url}/v1/payments/payment/{payment_id}/execute"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

        execute_data = {"payer_id": payer_id}

        try:
            response = requests.post(url, headers=headers, json=execute_data)
            response.raise_for_status()

            execution_response = response.json()

            return True, {
                "payment_id": execution_response.get("id"),
                "status": execution_response.get("state"),
                "transactions": execution_response.get("transactions", []),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"PayPal payment execution error: {str(e)}")
            return False, _("فشل في تنفيذ عملية الدفع")


class PaymobService:
    """Service for handling Paymob payments"""

    def __init__(self):
        # Get Paymob configuration from django-constance
        self.api_key = getattr(config, "PAYMOB_API_KEY", "")
        self.integration_id = getattr(config, "PAYMOB_INTEGRATION_ID", "")
        self.iframe_id = getattr(config, "PAYMOB_IFRAME_ID", "")
        self.base_url = "https://accept.paymob.com/api"
        self.auth_token = None
        self.token_expires = None

        if not self.api_key:
            logger.warning("Paymob API key not configured in django-constance")

    def get_auth_token(self):
        """Get Paymob authentication token"""
        if (
            self.auth_token
            and self.token_expires
            and timezone.now() < self.token_expires
        ):
            return self.auth_token

        url = f"{self.base_url}/auth/tokens"
        data = {"api_key": self.api_key}

        try:
            response = requests.post(url, json=data)
            response.raise_for_status()

            token_data = response.json()
            self.auth_token = token_data.get("token")
            # Paymob tokens typically last 1 hour
            self.token_expires = timezone.now() + timedelta(hours=1)

            return self.auth_token

        except requests.exceptions.RequestException as e:
            logger.error(f"Paymob auth error: {str(e)}")
            return None

    def create_order(self, amount_cents, currency="EGP"):
        """Create a Paymob order"""
        auth_token = self.get_auth_token()
        if not auth_token:
            return False, _("فشل في الاتصال بـ Paymob")

        url = f"{self.base_url}/ecommerce/orders"
        headers = {
            "Content-Type": "application/json",
        }

        order_data = {
            "auth_token": auth_token,
            "delivery_needed": "false",
            "amount_cents": str(amount_cents),
            "currency": currency,
            "items": [],
        }

        try:
            response = requests.post(url, headers=headers, json=order_data)
            response.raise_for_status()

            order_response = response.json()
            return True, order_response

        except requests.exceptions.RequestException as e:
            logger.error(f"Paymob order creation error: {str(e)}")
            return False, _("فشل في إنشاء الطلب")

    def get_payment_key(self, order_id, amount_cents, billing_data):
        """Get payment key for Paymob iframe"""
        auth_token = self.get_auth_token()
        if not auth_token:
            return False, _("فشل في الاتصال بـ Paymob")

        url = f"{self.base_url}/acceptance/payment_keys"
        headers = {
            "Content-Type": "application/json",
        }

        payment_data = {
            "auth_token": auth_token,
            "amount_cents": str(amount_cents),
            "expiration": 3600,  # 1 hour
            "order_id": order_id,
            "billing_data": billing_data,
            "currency": "EGP",
            "integration_id": self.integration_id,
        }

        try:
            response = requests.post(url, headers=headers, json=payment_data)
            response.raise_for_status()

            key_response = response.json()
            return True, key_response.get("token")

        except requests.exceptions.RequestException as e:
            logger.error(f"Paymob payment key error: {str(e)}")
            return False, _("فشل في الحصول على مفتاح الدفع")

    def create_payment_url(
        self, amount, currency="EGP", user_data=None, integration_id=None
    ):
        """Create complete payment flow and return iframe URL"""
        # Use custom integration ID or default
        if integration_id is None:
            integration_id = self.integration_id

        # Convert amount to cents
        amount_cents = int(float(amount) * 100)

        # Create order
        success, order_data = self.create_order(amount_cents, currency)
        if not success:
            return False, order_data

        order_id = order_data.get("id")

        # Prepare billing data
        billing_data = {
            "apartment": "NA",
            "email": (
                user_data.get("email", "user@example.com")
                if user_data
                else "user@example.com"
            ),
            "floor": "NA",
            "first_name": user_data.get("first_name", "User") if user_data else "User",
            "street": "NA",
            "building": "NA",
            "phone_number": (
                user_data.get("phone", "+201000000000")
                if user_data
                else "+201000000000"
            ),
            "shipping_method": "NA",
            "postal_code": "NA",
            "city": "NA",
            "country": "EG",
            "last_name": user_data.get("last_name", "Name") if user_data else "Name",
            "state": "NA",
        }

        # Get payment key with custom integration ID
        auth_token = self.get_auth_token()
        if not auth_token:
            return False, _("فشل في الاتصال بـ Paymob")

        url = f"{self.base_url}/acceptance/payment_keys"
        headers = {
            "Content-Type": "application/json",
        }

        payment_data = {
            "auth_token": auth_token,
            "amount_cents": str(amount_cents),
            "expiration": 3600,
            "order_id": order_id,
            "billing_data": billing_data,
            "currency": currency,
            "integration_id": integration_id,
        }

        try:
            response = requests.post(url, headers=headers, json=payment_data)
            response.raise_for_status()
            payment_response = response.json()
            payment_key = payment_response.get("token")
        except requests.exceptions.RequestException as e:
            logger.error(f"Paymob payment key error: {str(e)}")
            return False, _("فشل في إنشاء مفتاح الدفع")

        # Create iframe URL
        iframe_url = f"https://accept.paymob.com/api/acceptance/iframes/{self.iframe_id}?payment_token={payment_key}"

        return True, {
            "order_id": order_id,
            "payment_key": payment_key,
            "iframe_url": iframe_url,
        }


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
            return self.paypal.create_payment(
                amount=amount,
                currency=currency,
                description=description,
                return_url=kwargs.get("return_url"),
                cancel_url=kwargs.get("cancel_url"),
            )
        elif provider == "paymob":
            return self.paymob.create_payment_url(
                amount=amount, currency=currency, user_data=user_data
            )
        elif provider in ["mastercard", "visa"]:
            # Both Mastercard and Visa redirect to Paymob payment page
            return self.paymob.create_payment_url(
                amount=amount, currency=currency, user_data=user_data
            )
        else:
            return False, _("مزود الدفع غير مدعوم")

    def get_supported_providers(self):
        """Get list of supported payment providers based on django-constance configuration"""
        providers = []

        # Check PayPal configuration from constance
        paypal_client_id = getattr(config, "PAYPAL_CLIENT_ID", "")
        paypal_client_secret = getattr(config, "PAYPAL_CLIENT_SECRET", "")

        if paypal_client_id and paypal_client_secret:
            providers.append(
                {
                    "id": "paypal",
                    "name": "PayPal",
                    "currencies": ["USD", "EUR", "SAR"],
                    "icon": "fab fa-paypal",
                    "mode": getattr(config, "PAYPAL_MODE", "sandbox"),
                }
            )

        # Check Paymob configuration from constance
        paymob_api_key = getattr(config, "PAYMOB_API_KEY", "")
        paymob_integration_id = getattr(config, "PAYMOB_INTEGRATION_ID", "")

        if paymob_api_key and paymob_integration_id:
            providers.append(
                {
                    "id": "paymob",
                    "name": "Paymob",
                    "currencies": ["EGP", "SAR"],
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
