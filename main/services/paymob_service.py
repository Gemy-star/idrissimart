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
        enabled = config.PAYMOB_ENABLED
        has_secret = bool(config.PAYMOB_SECRET_KEY)
        # Accept any configured integration ID (card, wallet, visa, mastercard)
        has_integration = bool(config.PAYMOB_INTEGRATION_ID) or bool(
            getattr(config, "PAYMOB_WALLET_INTEGRATION_ID", "")
        )
        if not (enabled and has_secret and has_integration):
            logger.warning(
                "Paymob disabled — PAYMOB_ENABLED=%s, SECRET_KEY=%s, any_INTEGRATION_ID=%s",
                enabled,
                "set" if has_secret else "MISSING",
                "set" if has_integration else "MISSING",
            )
        return enabled and has_secret and has_integration

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
        currency: str = None,
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
            currency=currency,
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
    # Mobile Wallet payment request (Paymob v2 legacy API)
    # Sends a push/OTP to the customer's Vodafone Cash / Orange Money phone
    # ------------------------------------------------------------------

    @staticmethod
    def create_wallet_payment_request(
        amount: Decimal,
        order_id: str,
        billing_data: Dict,
        wallet_phone: str,
        currency: str = None,
        notification_url: str = None,
        redirection_url: str = None,
    ) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
        """
        Send a mobile-wallet payment request (Paymob v2 API).

        The customer receives a push-notification / OTP on their phone.

        Returns:
            (True,  redirect_url_or_None, None,  order_id)  on success (request sent)
            (False, None,                 error, None)       on failure
        """
        api_key = getattr(config, "PAYMOB_API_KEY", "")
        wallet_integration_id = getattr(config, "PAYMOB_WALLET_INTEGRATION_ID", "")
        if not api_key:
            return False, None, "PAYMOB_API_KEY not configured", None
        if not wallet_integration_id:
            return False, None, "PAYMOB_WALLET_INTEGRATION_ID not configured", None
        if currency is None:
            currency = getattr(config, "PAYMOB_CURRENCY", "EGP")

        amount_cents = int(amount * 100)
        headers = {"Content-Type": "application/json"}

        # Step 1 — auth token
        try:
            auth_resp = requests.post(
                "https://accept.paymob.com/api/auth/tokens",
                json={"api_key": api_key},
                headers=headers,
                timeout=15,
            )
            if not auth_resp.ok:
                return False, None, f"Paymob auth failed {auth_resp.status_code}", None
            auth_token = auth_resp.json().get("token")
            if not auth_token:
                return False, None, "Paymob auth: no token returned", None
        except requests.exceptions.RequestException as e:
            logger.error(f"Paymob wallet auth error: {e}")
            return False, None, str(e), None

        # Step 2 — create order
        try:
            order_payload = {
                "auth_token": auth_token,
                "delivery_needed": False,
                "amount_cents": amount_cents,
                "currency": currency,
                "merchant_order_id": order_id,
                "items": [],
            }
            if notification_url:
                order_payload["notify_url"] = notification_url

            order_resp = requests.post(
                "https://accept.paymob.com/api/ecommerce/orders",
                json=order_payload,
                headers=headers,
                timeout=15,
            )
            if not order_resp.ok:
                return False, None, f"Paymob order creation failed {order_resp.status_code}", None
            paymob_order_id = str(order_resp.json().get("id", ""))
        except requests.exceptions.RequestException as e:
            logger.error(f"Paymob wallet order error: {e}")
            return False, None, str(e), None

        # Step 3 — payment key
        required_billing = [
            "apartment", "email", "floor", "first_name", "street",
            "building", "phone_number", "postal_code", "city",
            "country", "last_name", "state",
        ]
        safe_billing = {k: billing_data.get(k) or "NA" for k in required_billing}
        safe_billing["phone_number"] = wallet_phone  # ensure wallet phone is used

        try:
            key_payload = {
                "auth_token": auth_token,
                "amount_cents": amount_cents,
                "expiration": 3600,
                "order_id": paymob_order_id,
                "billing_data": safe_billing,
                "currency": currency,
                "integration_id": int(wallet_integration_id),
            }
            if notification_url:
                key_payload["lock_order_when_paid"] = True

            key_resp = requests.post(
                "https://accept.paymob.com/api/acceptance/payment_keys",
                json=key_payload,
                headers=headers,
                timeout=15,
            )
            if not key_resp.ok:
                return False, None, f"Paymob payment key failed {key_resp.status_code}", None
            payment_token = key_resp.json().get("token")
            if not payment_token:
                return False, None, "Paymob payment key: no token returned", None
        except requests.exceptions.RequestException as e:
            logger.error(f"Paymob wallet payment key error: {e}")
            return False, None, str(e), None

        # Step 4 — send wallet payment request to phone
        try:
            pay_resp = requests.post(
                "https://accept.paymob.com/api/acceptance/payments/pay",
                json={
                    "source": {"identifier": wallet_phone, "subtype": "WALLET"},
                    "payment_token": payment_token,
                },
                headers=headers,
                timeout=20,
            )
            pay_data = pay_resp.json()
            if not pay_resp.ok:
                detail = pay_data.get("detail") or pay_resp.text
                return False, None, f"Paymob wallet pay failed: {detail}", None

            redirect_url = pay_data.get("redirect_url") or redirection_url
            logger.info(
                "Paymob wallet pay request sent — order=%s phone=%s pending=%s",
                paymob_order_id,
                wallet_phone,
                pay_data.get("pending"),
            )
            return True, redirect_url, None, paymob_order_id

        except requests.exceptions.RequestException as e:
            logger.error(f"Paymob wallet pay request error: {e}")
            return False, None, str(e), None

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
