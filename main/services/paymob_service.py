"""
Paymob Payment Gateway Service — New v1 Unified Checkout API
Uses PAYMOB_SECRET_KEY (egy_sk_...) instead of the legacy API key + 3-step flow.
"""

import hashlib
import hmac
import logging
from decimal import Decimal
from typing import Dict, Optional, Tuple

import requests
from constance import config

logger = logging.getLogger(__name__)


class PaymobService:
    """Service for processing payments via Paymob (v1 Unified Checkout)"""

    INTENTION_URL = "https://accept.paymob.com/v1/intention/"
    CHECKOUT_URL  = "https://accept.paymob.com/unifiedcheckout/"

    @staticmethod
    def is_enabled() -> bool:
        """Check if Paymob payment gateway is enabled"""
        return (
            config.PAYMOB_ENABLED
            and bool(config.PAYMOB_SECRET_KEY)
            and bool(config.PAYMOB_INTEGRATION_ID)
        )

    # ------------------------------------------------------------------
    # New v1 API — single intention call
    # ------------------------------------------------------------------

    @staticmethod
    def create_intention(
        amount_cents: int,
        order_id: str,
        billing_data: Dict,
        items: list = None,
        integration_id: str = None,
        currency: str = None,
        notification_url: str = None,
        redirection_url: str = None,
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Create a payment intention via Paymob v1 API.

        Returns:
            (True, intention_data, None)  on success
            (False, None, error_message) on failure
        """
        secret_key = config.PAYMOB_SECRET_KEY
        if not secret_key:
            return False, None, "PAYMOB_SECRET_KEY not configured"

        if integration_id is None:
            integration_id = config.PAYMOB_INTEGRATION_ID
        if currency is None:
            currency = getattr(config, "PAYMOB_CURRENCY", "EGP")

        # billing_data must have all required fields; fill missing with "NA"
        required_billing = [
            "apartment", "email", "floor", "first_name", "street",
            "building", "phone_number", "postal_code", "city",
            "country", "last_name", "state",
        ]
        safe_billing = {k: billing_data.get(k) or "NA" for k in required_billing}

        payload = {
            "amount": amount_cents,
            "currency": currency,
            "payment_methods": [int(integration_id)],
            "items": items or [],
            "billing_data": safe_billing,
            "customer": {
                "first_name": safe_billing["first_name"],
                "last_name":  safe_billing["last_name"],
                "email":      safe_billing["email"],
            },
            "extras": {"merchant_order_id": order_id},
        }

        if notification_url:
            payload["notification_url"] = notification_url
        if redirection_url:
            payload["redirection_url"] = redirection_url

        headers = {
            "Authorization": f"Token {secret_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(PaymobService.INTENTION_URL, json=payload, headers=headers)

            if not response.ok:
                logger.error(
                    f"Paymob create_intention failed {response.status_code}: {response.text}"
                )
                try:
                    detail = response.json().get("detail") or response.text
                except Exception:
                    detail = response.text
                return False, None, f"Paymob error {response.status_code}: {detail}"

            data = response.json()
            logger.info(f"Paymob intention created: id={data.get('id')}")
            return True, data, None

        except requests.exceptions.RequestException as e:
            logger.error(f"Paymob create_intention request failed: {e}")
            return False, None, str(e)

    @staticmethod
    def get_checkout_url(client_secret: str) -> str:
        """Build the Unified Checkout redirect URL from a client_secret."""
        public_key = config.PAYMOB_PUBLIC_KEY
        return f"{PaymobService.CHECKOUT_URL}?publicKey={public_key}&clientSecret={client_secret}"

    # ------------------------------------------------------------------
    # Main entry-point (replaces the old 3-step process_payment)
    # ------------------------------------------------------------------

    @staticmethod
    def process_payment(
        amount: Decimal,
        order_id: str,
        billing_data: Dict,
        items: list = None,
        integration_id: str = None,
        notification_url: str = None,
        redirection_url: str = None,
    ) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
        """
        Create a Paymob payment and return the checkout URL.

        Returns:
            (True,  checkout_url, None,          intention_id)  on success
            (False, None,         error_message, None)          on failure
        """
        if not PaymobService.is_enabled():
            return False, None, "Paymob payment gateway is disabled", None

        amount_cents = int(amount * 100)

        success, data, error = PaymobService.create_intention(
            amount_cents=amount_cents,
            order_id=order_id,
            billing_data=billing_data,
            items=items,
            integration_id=integration_id,
            notification_url=notification_url,
            redirection_url=redirection_url,
        )

        if not success:
            return False, None, error, None

        client_secret = data.get("client_secret")
        if not client_secret:
            logger.error(f"No client_secret in Paymob intention response: {data}")
            return False, None, "No client_secret in Paymob response", None

        intention_id = data.get("id")
        checkout_url = PaymobService.get_checkout_url(client_secret)

        logger.info(f"Paymob checkout URL generated for order {order_id}")
        return True, checkout_url, None, str(intention_id) if intention_id else None

    # ------------------------------------------------------------------
    # HMAC verification for Paymob transaction callbacks
    # ------------------------------------------------------------------

    @staticmethod
    def verify_hmac(data: Dict) -> bool:
        """Verify HMAC signature from Paymob callback (legacy + new API)."""
        if not config.PAYMOB_HMAC_SECRET:
            logger.warning("Paymob HMAC secret not configured — skipping verification")
            return True  # allow if not configured rather than hard-fail

        try:
            received_hmac = data.get("hmac")
            if not received_hmac:
                logger.error("No HMAC in callback data")
                return False

            concatenated_string = (
                f"{data.get('amount_cents', '')}"
                f"{data.get('created_at', '')}"
                f"{data.get('currency', '')}"
                f"{data.get('error_occured', '')}"
                f"{data.get('has_parent_transaction', '')}"
                f"{data.get('id', '')}"
                f"{data.get('integration_id', '')}"
                f"{data.get('is_3d_secure', '')}"
                f"{data.get('is_auth', '')}"
                f"{data.get('is_capture', '')}"
                f"{data.get('is_refunded', '')}"
                f"{data.get('is_standalone_payment', '')}"
                f"{data.get('is_voided', '')}"
                f"{data.get('order', {}).get('id', '')}"
                f"{data.get('owner', '')}"
                f"{data.get('pending', '')}"
                f"{data.get('source_data', {}).get('pan', '')}"
                f"{data.get('source_data', {}).get('sub_type', '')}"
                f"{data.get('source_data', {}).get('type', '')}"
                f"{data.get('success', '')}"
            )

            calculated_hmac = hmac.new(
                config.PAYMOB_HMAC_SECRET.encode("utf-8"),
                concatenated_string.encode("utf-8"),
                hashlib.sha512,
            ).hexdigest()

            is_valid = hmac.compare_digest(calculated_hmac, received_hmac)
            if not is_valid:
                logger.error("Paymob HMAC verification failed")
            return is_valid

        except Exception as e:
            logger.error(f"Error verifying Paymob HMAC: {e}")
            return False

    # ------------------------------------------------------------------
    # Refund
    # ------------------------------------------------------------------

    @staticmethod
    def refund_transaction(transaction_id: str, amount_cents: int) -> bool:
        """Refund a captured transaction using the v1 API."""
        secret_key = config.PAYMOB_SECRET_KEY
        if not secret_key:
            logger.error("PAYMOB_SECRET_KEY not configured")
            return False

        try:
            url = f"https://accept.paymob.com/v1/transactions/{transaction_id}/refund/"
            headers = {
                "Authorization": f"Token {secret_key}",
                "Content-Type": "application/json",
            }
            payload = {"amount_cents": amount_cents}

            response = requests.post(url, json=payload, headers=headers)

            if not response.ok:
                logger.error(f"Paymob refund failed {response.status_code}: {response.text}")
                return False

            logger.info(f"Paymob refund processed for transaction {transaction_id}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to process Paymob refund: {e}")
            return False
