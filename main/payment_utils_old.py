"""Payment utilities for filtering allowed payment methods"""

from django.utils.translation import gettext_lazy as _


class PaymentContext:
    """Payment context types"""
    PLATFORM_PAYMENT = "platform"  # User paying to platform (packages, ad fees, features)
    CART_PURCHASE = "cart"  # User buying from another user via cart


def get_allowed_payment_methods(context=PaymentContext.PLATFORM_PAYMENT):
    """
    Get allowed payment methods based on payment context.

    Args:
        context: Payment context (platform or cart)

    Returns:
        List of tuples (value, label) for allowed payment methods
    """

    # All available payment methods
    ALL_METHODS = [
        ("visa", _("بطاقة فيزا/ماستركارد - Visa/Mastercard")),
        ("wallet", _("محفظة إلكترونية - E-Wallet")),
        ("instapay", _("إنستاباي - InstaPay")),
        ("cod", _("الدفع عند الاستلام - Cash on Delivery")),
        ("partial", _("دفع جزئي - Partial Payment")),
    ]

    if context == PaymentContext.PLATFORM_PAYMENT:
        # For platform payments: Only online methods allowed
        # User paying to platform for packages, ad fees, features
        return [
            ("visa", _("بطاقة فيزا/ماستركارد - Visa/Mastercard")),
            ("wallet", _("محفظة إلكترونية - E-Wallet")),
            ("instapay", _("إنستاباي - InstaPay")),
        ]

    elif context == PaymentContext.CART_PURCHASE:
        # For cart purchases: All methods allowed
        # User buying from another user
        return ALL_METHODS

    else:
        # Default: online methods only
        return [
            ("visa", _("بطاقة فيزا/ماستركارد - Visa/Mastercard")),
            ("wallet", _("محفظة إلكترونية - E-Wallet")),
            ("instapay", _("إنستاباي - InstaPay")),
        ]


def is_payment_method_allowed(payment_method, context=PaymentContext.PLATFORM_PAYMENT):
    """
    Check if a payment method is allowed for the given context.

    Args:
        payment_method: Payment method to check
        context: Payment context

    Returns:
        bool: True if allowed, False otherwise
    """
    allowed_methods = get_allowed_payment_methods(context)
    allowed_values = [method[0] for method in allowed_methods]
    return payment_method in allowed_values


def get_payment_method_display(payment_method):
    """Get display name for payment method"""
    all_methods = {
        "visa": _("بطاقة فيزا/ماستركارد"),
        "wallet": _("محفظة إلكترونية"),
        "instapay": _("إنستاباي"),
        "cod": _("الدفع عند الاستلام"),
        "partial": _("دفع جزئي"),
    }
    return all_methods.get(payment_method, payment_method)
