"""
Paymob Payment Gateway Integration Module
Handles payment processing with Paymob Accept API
"""

import hashlib
import hmac
import json
import requests
from django.conf import settings
from typing import Dict, Optional


class PaymobClient:
    """Client for interacting with Paymob Accept API."""

    def __init__(self):
        self.api_key = settings.PAYMOB_API_KEY
        self.secret_key = settings.PAYMOB_SECRET_KEY
        self.public_key = settings.PAYMOB_PUBLIC_KEY
        self.iframe_id = settings.PAYMOB_IFRAME_ID
        self.integration_id = settings.PAYMOB_INTEGRATION_ID
        self.hmac_secret = settings.PAYMOB_HMAC_SECRET
        self.base_url = settings.PAYMOB_BASE_URL

    def authenticate(self) -> Optional[str]:
        """
        Authenticate with Paymob API and get authentication token.

        Returns:
            str: Authentication token or None if authentication fails
        """
        url = f"{self.base_url}/auth/tokens"
        payload = {"api_key": self.api_key}

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("token")
        except requests.exceptions.RequestException as e:
            print(f"Paymob authentication error: {e}")
            return None

    def create_order(self, auth_token: str, amount_cents: int,
                     merchant_order_id: str, items: list = None) -> Optional[Dict]:
        """
        Create an order with Paymob.

        Args:
            auth_token: Authentication token from authenticate()
            amount_cents: Amount in cents (e.g., 100 EGP = 10000 cents)
            merchant_order_id: Your internal order ID
            items: List of items in the order (optional)

        Returns:
            dict: Order data or None if creation fails
        """
        url = f"{self.base_url}/ecommerce/orders"
        payload = {
            "auth_token": auth_token,
            "delivery_needed": "false",
            "amount_cents": amount_cents,
            "currency": "EGP",
            "merchant_order_id": merchant_order_id,
            "items": items or []
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Paymob order creation error: {e}")
            return None

    def create_payment_key(self, auth_token: str, order_id: int,
                           amount_cents: int, billing_data: Dict) -> Optional[str]:
        """
        Create a payment key for processing payment.

        Args:
            auth_token: Authentication token
            order_id: Order ID from create_order()
            amount_cents: Amount in cents
            billing_data: Customer billing information

        Returns:
            str: Payment key or None if creation fails
        """
        url = f"{self.base_url}/acceptance/payment_keys"
        payload = {
            "auth_token": auth_token,
            "amount_cents": amount_cents,
            "expiration": 3600,
            "order_id": order_id,
            "billing_data": billing_data,
            "currency": "EGP",
            "integration_id": self.integration_id
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("token")
        except requests.exceptions.RequestException as e:
            print(f"Paymob payment key creation error: {e}")
            return None

    def verify_hmac(self, data: Dict) -> bool:
        """
        Verify HMAC signature from Paymob callback.

        Args:
            data: Callback data from Paymob

        Returns:
            bool: True if signature is valid, False otherwise
        """
        if not self.hmac_secret:
            print("Warning: HMAC secret not configured")
            return False

        received_hmac = data.get('hmac')
        if not received_hmac:
            return False

        # Construct the concatenated string according to Paymob documentation
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
            self.hmac_secret.encode(),
            concatenated_string.encode(),
            hashlib.sha512
        ).hexdigest()

        return hmac.compare_digest(calculated_hmac, received_hmac)

    def process_payment(self, order_id: str, amount: float,
                        billing_data: Dict) -> Optional[str]:
        """
        Complete payment flow and return payment URL.

        Args:
            order_id: Your internal order ID
            amount: Amount in your currency (will be converted to cents)
            billing_data: Customer billing information

        Returns:
            str: Payment iframe URL or None if process fails
        """
        # Convert amount to cents
        amount_cents = int(amount * 100)

        # Step 1: Authenticate
        auth_token = self.authenticate()
        if not auth_token:
            return None

        # Step 2: Create order
        order_data = self.create_order(
            auth_token=auth_token,
            amount_cents=amount_cents,
            merchant_order_id=order_id
        )
        if not order_data:
            return None

        paymob_order_id = order_data.get("id")

        # Step 3: Create payment key
        payment_key = self.create_payment_key(
            auth_token=auth_token,
            order_id=paymob_order_id,
            amount_cents=amount_cents,
            billing_data=billing_data
        )
        if not payment_key:
            return None

        # Return iframe URL
        return f"https://accept.paymob.com/api/acceptance/iframes/{self.iframe_id}?payment_token={payment_key}"


def get_billing_data(user, email: str = None, phone: str = None) -> Dict:
    """
    Helper function to construct billing data from user object.

    Args:
        user: Django user object
        email: Override email
        phone: Override phone

    Returns:
        dict: Billing data dictionary
    """
    return {
        "apartment": "NA",
        "email": email or getattr(user, 'email', 'NA'),
        "floor": "NA",
        "first_name": getattr(user, 'first_name', 'Customer'),
        "street": "NA",
        "building": "NA",
        "phone_number": phone or getattr(user, 'phone', 'NA'),
        "shipping_method": "NA",
        "postal_code": "NA",
        "city": "NA",
        "country": "EG",
        "last_name": getattr(user, 'last_name', ''),
        "state": "NA"
    }
