"""
Paymob Payment Gateway Helper Functions
This module provides helper functions for Paymob integration.
The main PaymobService class is in main.services.paymob_service
"""

from typing import Dict


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
        "email": email or getattr(user, "email", "NA"),
        "floor": "NA",
        "first_name": getattr(user, "first_name", "Customer"),
        "street": "NA",
        "building": "NA",
        "phone_number": phone or getattr(user, "phone", "NA"),
        "shipping_method": "NA",
        "postal_code": "NA",
        "city": "NA",
        "country": "EG",
        "last_name": getattr(user, "last_name", ""),
        "state": "NA",
    }
