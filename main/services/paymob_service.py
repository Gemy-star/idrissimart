"""
Paymob Payment Gateway Service
Integrates with django-constance for dynamic configuration
"""

import hashlib
import hmac
import json
import logging
from decimal import Decimal
from typing import Dict, Optional, Tuple

import requests
from constance import config
from django.conf import settings

logger = logging.getLogger(__name__)


class PaymobService:
    """Service for processing payments via Paymob"""

    BASE_URL = "https://accept.paymob.com/api"

    @staticmethod
    def is_enabled() -> bool:
        """Check if Paymob payment gateway is enabled"""
        return (
            config.PAYMOB_ENABLED
            and bool(config.PAYMOB_API_KEY)
            and bool(config.PAYMOB_INTEGRATION_ID)
        )

    @staticmethod
    def authenticate() -> Optional[str]:
        """
        Authenticate with Paymob and get auth token

        Returns:
            str: Auth token or None if failed
        """
        if not config.PAYMOB_API_KEY:
            logger.error("Paymob API key not configured")
            return None

        try:
            url = f"{PaymobService.BASE_URL}/auth/tokens"
            payload = {"api_key": config.PAYMOB_API_KEY}

            response = requests.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            token = data.get("token")

            if token:
                logger.info("Paymob authentication successful")
                return token
            else:
                logger.error("No token in Paymob authentication response")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Paymob authentication failed: {str(e)}")
            return None

    @staticmethod
    def create_order(
        auth_token: str,
        amount_cents: int,
        currency: str = None,
        merchant_order_id: str = None,
        items: list = None,
    ) -> Optional[Dict]:
        """
        Create an order in Paymob

        Args:
            auth_token: Authentication token
            amount_cents: Amount in cents (e.g., 10000 for 100 EGP)
            currency: Currency code (default from config)
            merchant_order_id: Your order ID
            items: List of order items

        Returns:
            dict: Order data or None if failed
        """
        try:
            url = f"{PaymobService.BASE_URL}/ecommerce/orders"

            if currency is None:
                currency = config.PAYMOB_CURRENCY

            if items is None:
                items = []

            payload = {
                "auth_token": auth_token,
                "delivery_needed": "false",
                "amount_cents": str(amount_cents),
                "currency": currency,
                "merchant_order_id": merchant_order_id,
                "items": items,
            }

            response = requests.post(url, json=payload)
            response.raise_for_status()

            order_data = response.json()
            logger.info(f"Paymob order created: {order_data.get('id')}")
            return order_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create Paymob order: {str(e)}")
            return None

    @staticmethod
    def create_payment_key(
        auth_token: str,
        order_id: int,
        amount_cents: int,
        billing_data: Dict,
        currency: str = None,
        integration_id: str = None,
    ) -> Optional[str]:
        """
        Create payment key for checkout

        Args:
            auth_token: Authentication token
            order_id: Paymob order ID
            amount_cents: Amount in cents
            billing_data: Customer billing information
            currency: Currency code (default from config)
            integration_id: Integration ID (default from config)

        Returns:
            str: Payment key or None if failed
        """
        try:
            url = f"{PaymobService.BASE_URL}/acceptance/payment_keys"

            if currency is None:
                currency = config.PAYMOB_CURRENCY

            if integration_id is None:
                integration_id = config.PAYMOB_INTEGRATION_ID

            payload = {
                "auth_token": auth_token,
                "amount_cents": str(amount_cents),
                "expiration": 3600,  # 1 hour
                "order_id": str(order_id),
                "billing_data": billing_data,
                "currency": currency,
                "integration_id": integration_id,
            }

            response = requests.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            payment_key = data.get("token")

            if payment_key:
                logger.info("Paymob payment key created successfully")
                return payment_key
            else:
                logger.error("No payment key in Paymob response")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create Paymob payment key: {str(e)}")
            return None

    @staticmethod
    def get_iframe_url(payment_key: str, iframe_id: str = None) -> str:
        """
        Get iFrame URL for payment

        Args:
            payment_key: Payment key from create_payment_key
            iframe_id: iFrame ID (default from config)

        Returns:
            str: iFrame URL
        """
        if iframe_id is None:
            iframe_id = config.PAYMOB_IFRAME_ID

        return f"https://accept.paymob.com/api/acceptance/iframes/{iframe_id}?payment_token={payment_key}"

    @staticmethod
    def verify_hmac(data: Dict) -> bool:
        """
        Verify HMAC signature from Paymob callback

        Args:
            data: Callback data from Paymob

        Returns:
            bool: True if signature is valid, False otherwise
        """
        if not config.PAYMOB_HMAC_SECRET:
            logger.warning("Paymob HMAC secret not configured")
            return False

        try:
            # Extract HMAC from callback
            received_hmac = data.get("hmac")
            if not received_hmac:
                logger.error("No HMAC in callback data")
                return False

            # Build the string to hash (order matters!)
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

            # Calculate HMAC
            calculated_hmac = hmac.new(
                config.PAYMOB_HMAC_SECRET.encode("utf-8"),
                concatenated_string.encode("utf-8"),
                hashlib.sha512,
            ).hexdigest()

            # Compare
            is_valid = hmac.compare_digest(calculated_hmac, received_hmac)

            if not is_valid:
                logger.error("HMAC verification failed")

            return is_valid

        except Exception as e:
            logger.error(f"Error verifying HMAC: {str(e)}")
            return False

    @staticmethod
    def process_payment(
        amount: Decimal,
        order_id: str,
        billing_data: Dict,
        items: list = None,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Process a complete payment flow

        Args:
            amount: Payment amount
            order_id: Your order ID
            billing_data: Customer billing information
            items: Order items

        Returns:
            Tuple of (success, payment_url, error_message)
        """
        if not PaymobService.is_enabled():
            return False, None, "Paymob payment gateway is disabled"

        try:
            # Step 1: Authenticate
            auth_token = PaymobService.authenticate()
            if not auth_token:
                return False, None, "Failed to authenticate with Paymob"

            # Convert amount to cents
            amount_cents = int(amount * 100)

            # Step 2: Create order
            order_data = PaymobService.create_order(
                auth_token=auth_token,
                amount_cents=amount_cents,
                merchant_order_id=order_id,
                items=items or [],
            )

            if not order_data:
                return False, None, "Failed to create Paymob order"

            paymob_order_id = order_data.get("id")

            # Step 3: Create payment key
            payment_key = PaymobService.create_payment_key(
                auth_token=auth_token,
                order_id=paymob_order_id,
                amount_cents=amount_cents,
                billing_data=billing_data,
            )

            if not payment_key:
                return False, None, "Failed to create payment key"

            # Step 4: Get payment URL
            payment_url = PaymobService.get_iframe_url(payment_key)

            logger.info(f"Paymob payment URL generated for order {order_id}")
            return True, payment_url, None

        except Exception as e:
            error_msg = f"Error processing Paymob payment: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg

    @staticmethod
    def refund_transaction(transaction_id: str, amount_cents: int) -> bool:
        """
        Refund a transaction

        Args:
            transaction_id: Paymob transaction ID
            amount_cents: Amount to refund in cents

        Returns:
            bool: True if refund successful, False otherwise
        """
        try:
            auth_token = PaymobService.authenticate()
            if not auth_token:
                return False

            url = f"{PaymobService.BASE_URL}/acceptance/void_refund/refund"
            payload = {
                "auth_token": auth_token,
                "transaction_id": transaction_id,
                "amount_cents": amount_cents,
            }

            response = requests.post(url, json=payload)
            response.raise_for_status()

            logger.info(f"Refund processed for transaction {transaction_id}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to process refund: {str(e)}")
            return False
