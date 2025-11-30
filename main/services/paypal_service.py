"""
PayPal Payment Gateway Service
Integrates with django-constance for dynamic configuration
"""

import logging
from decimal import Decimal
from typing import Dict, Optional, Tuple

import requests
from constance import config
from django.conf import settings

logger = logging.getLogger(__name__)


class PayPalService:
    """Service for processing payments via PayPal"""

    SANDBOX_URL = "https://api-m.sandbox.paypal.com"
    LIVE_URL = "https://api-m.paypal.com"

    @staticmethod
    def get_base_url() -> str:
        """Get base URL based on mode (sandbox or live)"""
        mode = config.PAYPAL_MODE.lower()
        return (
            PayPalService.SANDBOX_URL if mode == "sandbox" else PayPalService.LIVE_URL
        )

    @staticmethod
    def is_enabled() -> bool:
        """Check if PayPal payment gateway is enabled"""
        return bool(config.PAYPAL_CLIENT_ID) and bool(config.PAYPAL_CLIENT_SECRET)

    @staticmethod
    def get_access_token() -> Optional[str]:
        """
        Get OAuth access token from PayPal

        Returns:
            str: Access token or None if failed
        """
        if not PayPalService.is_enabled():
            logger.error("PayPal credentials not configured")
            return None

        try:
            url = f"{PayPalService.get_base_url()}/v1/oauth2/token"

            headers = {"Accept": "application/json", "Accept-Language": "en_US"}

            data = {"grant_type": "client_credentials"}

            response = requests.post(
                url,
                headers=headers,
                data=data,
                auth=(config.PAYPAL_CLIENT_ID, config.PAYPAL_CLIENT_SECRET),
            )

            response.raise_for_status()

            token_data = response.json()
            access_token = token_data.get("access_token")

            if access_token:
                logger.info("PayPal access token obtained successfully")
                return access_token
            else:
                logger.error("No access token in PayPal response")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get PayPal access token: {str(e)}")
            return None

    @staticmethod
    def create_order(
        amount: Decimal,
        currency: str = "USD",
        order_id: str = None,
        description: str = None,
        return_url: str = None,
        cancel_url: str = None,
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Create a PayPal order

        Args:
            amount: Payment amount
            currency: Currency code (default: USD)
            order_id: Your order reference ID
            description: Payment description
            return_url: URL to redirect after successful payment
            cancel_url: URL to redirect if payment is cancelled

        Returns:
            Tuple of (success, order_data, error_message)
        """
        if not PayPalService.is_enabled():
            return False, None, "PayPal payment gateway is disabled"

        try:
            access_token = PayPalService.get_access_token()
            if not access_token:
                return False, None, "Failed to get PayPal access token"

            url = f"{PayPalService.get_base_url()}/v2/checkout/orders"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }

            # Format amount to 2 decimal places
            amount_str = f"{float(amount):.2f}"

            payload = {
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "reference_id": order_id or "default",
                        "description": description or f"Order from {config.SITE_NAME}",
                        "amount": {"currency_code": currency, "value": amount_str},
                    }
                ],
                "application_context": {
                    "brand_name": config.SITE_NAME,
                    "landing_page": "BILLING",
                    "user_action": "PAY_NOW",
                },
            }

            # Add return and cancel URLs if provided
            if return_url:
                payload["application_context"]["return_url"] = return_url
            if cancel_url:
                payload["application_context"]["cancel_url"] = cancel_url

            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            order_data = response.json()
            logger.info(f"PayPal order created: {order_data.get('id')}")

            return True, order_data, None

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to create PayPal order: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg

    @staticmethod
    def capture_order(order_id: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Capture an approved PayPal order

        Args:
            order_id: PayPal order ID

        Returns:
            Tuple of (success, capture_data, error_message)
        """
        try:
            access_token = PayPalService.get_access_token()
            if not access_token:
                return False, None, "Failed to get PayPal access token"

            url = (
                f"{PayPalService.get_base_url()}/v2/checkout/orders/{order_id}/capture"
            )

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }

            response = requests.post(url, headers=headers)
            response.raise_for_status()

            capture_data = response.json()
            logger.info(f"PayPal order captured: {order_id}")

            return True, capture_data, None

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to capture PayPal order: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg

    @staticmethod
    def get_order_details(order_id: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Get details of a PayPal order

        Args:
            order_id: PayPal order ID

        Returns:
            Tuple of (success, order_data, error_message)
        """
        try:
            access_token = PayPalService.get_access_token()
            if not access_token:
                return False, None, "Failed to get PayPal access token"

            url = f"{PayPalService.get_base_url()}/v2/checkout/orders/{order_id}"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            order_data = response.json()
            return True, order_data, None

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to get PayPal order details: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg

    @staticmethod
    def get_approval_url(order_data: Dict) -> Optional[str]:
        """
        Extract approval URL from order data

        Args:
            order_data: PayPal order response data

        Returns:
            str: Approval URL or None if not found
        """
        links = order_data.get("links", [])
        for link in links:
            if link.get("rel") == "approve":
                return link.get("href")
        return None

    @staticmethod
    def process_payment(
        amount: Decimal,
        order_id: str,
        description: str = None,
        return_url: str = None,
        cancel_url: str = None,
        currency: str = "USD",
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Process a complete payment flow and get approval URL

        Args:
            amount: Payment amount
            order_id: Your order ID
            description: Payment description
            return_url: URL to redirect after successful payment
            cancel_url: URL to redirect if payment is cancelled
            currency: Currency code

        Returns:
            Tuple of (success, approval_url, error_message)
        """
        success, order_data, error = PayPalService.create_order(
            amount=amount,
            currency=currency,
            order_id=order_id,
            description=description,
            return_url=return_url,
            cancel_url=cancel_url,
        )

        if not success:
            return False, None, error

        approval_url = PayPalService.get_approval_url(order_data)
        if not approval_url:
            return False, None, "Failed to get PayPal approval URL"

        logger.info(f"PayPal payment URL generated for order {order_id}")
        return True, approval_url, None

    @staticmethod
    def refund_capture(
        capture_id: str, amount: Optional[Decimal] = None, currency: str = "USD"
    ) -> bool:
        """
        Refund a captured payment

        Args:
            capture_id: PayPal capture ID
            amount: Amount to refund (optional, full refund if not specified)
            currency: Currency code

        Returns:
            bool: True if refund successful, False otherwise
        """
        try:
            access_token = PayPalService.get_access_token()
            if not access_token:
                return False

            url = f"{PayPalService.get_base_url()}/v2/payments/captures/{capture_id}/refund"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }

            payload = {}
            if amount is not None:
                payload["amount"] = {
                    "currency_code": currency,
                    "value": f"{float(amount):.2f}",
                }

            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            logger.info(f"PayPal refund processed for capture {capture_id}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to process PayPal refund: {str(e)}")
            return False
