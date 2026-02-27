"""Payment utilities for filtering allowed payment methods"""

from django.utils.translation import gettext_lazy as _


class PaymentContext:
    """
    Payment context types - maps to PaymentMethodConfig.context
    """
    AD_POSTING = "ad_posting"
    AD_UPGRADE = "ad_upgrade"
    PACKAGE_PURCHASE = "package_purchase"
    PRODUCT_PURCHASE = "product_purchase"

    # Legacy support
    PLATFORM_PAYMENT = "ad_posting"  # Backwards compatibility
    CART_PURCHASE = "product_purchase"  # Backwards compatibility


def get_allowed_payment_methods(context=PaymentContext.AD_POSTING):
    """
    Get allowed payment methods based on payment context.
    Now reads from database PaymentMethodConfig and respects global payment settings.

    Args:
        context: Payment context (ad_posting, ad_upgrade, package_purchase, product_purchase)

    Returns:
        List of tuples (value, label) for allowed payment methods
    """
    try:
        from content.models import PaymentMethodConfig, SiteConfiguration
        from constance import config as constance_config

        # Map legacy contexts to new contexts
        context_map = {
            "platform": PaymentContext.AD_POSTING,
            "cart": PaymentContext.PRODUCT_PURCHASE,
        }
        context = context_map.get(context, context)

        # Get site configuration for global payment flags
        site_config = SiteConfiguration.get_solo()

        # Get config from database
        payment_config = PaymentMethodConfig.get_for_context(context)

        if not payment_config.is_active:
            # If config is disabled, return empty list
            return []

        # Get enabled methods from PaymentMethodConfig
        methods = payment_config.get_enabled_methods()

        # Filter based on global payment settings from SiteConfiguration
        filtered_methods = []
        for method_code, method_label in methods:
            # Online payment methods: visa, paypal, paymob
            if method_code in ["visa", "paypal", "paymob"]:
                # Check site_config.allow_online_payment (ALLOW_ONLINE_PAYMENT is in SiteConfiguration, not constance)
                if site_config.allow_online_payment:
                    # Additionally check if specific provider is enabled
                    if method_code == "paypal":
                        try:
                            from .services.paypal_service import PayPalService
                            if PayPalService.is_enabled():
                                filtered_methods.append((method_code, method_label))
                        except Exception:
                            pass
                    elif method_code in ["visa", "paymob"]:
                        if getattr(constance_config, "PAYMOB_ENABLED", True):
                            filtered_methods.append((method_code, method_label))
            # Offline payment methods: instapay, wallet
            elif method_code in ["instapay", "wallet"]:
                if site_config.allow_offline_payment:
                    filtered_methods.append((method_code, method_label))
            # COD and partial are for product purchase, controlled by PaymentMethodConfig
            elif method_code in ["cod", "partial"]:
                # These are already filtered by PaymentMethodConfig context
                filtered_methods.append((method_code, method_label))
            else:
                # Unknown methods, include them
                filtered_methods.append((method_code, method_label))

        return filtered_methods

    except Exception as e:
        # Fallback to hardcoded methods if DB not available (e.g., during migrations)
        print(f"Warning: Could not load payment config from DB: {e}")
        return _get_fallback_methods(context)


def _get_fallback_methods(context):
    """Fallback payment methods if database is not available"""
    if context in [PaymentContext.AD_POSTING, PaymentContext.AD_UPGRADE, PaymentContext.PACKAGE_PURCHASE]:
        # Platform payments: Online methods only
        return [
            ("visa", _("بطاقة فيزا/ماستركارد")),
            ("wallet", _("محفظة إلكترونية")),
            ("instapay", _("إنستا باي")),
        ]
    elif context == PaymentContext.PRODUCT_PURCHASE:
        # Product purchase: All methods
        return [
            ("visa", _("بطاقة فيزا/ماستركارد")),
            ("wallet", _("محفظة إلكترونية")),
            ("instapay", _("إنستا باي")),
            ("cod", _("الدفع عند الاستلام")),
            ("partial", _("دفع جزئي")),
        ]
    else:
        # Default: online methods
        return [
            ("visa", _("بطاقة فيزا/ماستركارد")),
            ("wallet", _("محفظة إلكترونية")),
            ("instapay", _("إنستا باي")),
        ]


def is_payment_method_allowed(payment_method, context=PaymentContext.AD_POSTING):
    """
    Check if a payment method is allowed for the given context.
    Also checks global payment settings from SiteConfiguration and constance.

    Args:
        payment_method: Payment method to check
        context: Payment context

    Returns:
        bool: True if allowed, False otherwise
    """
    try:
        from content.models import PaymentMethodConfig, SiteConfiguration
        from constance import config as constance_config

        # Map legacy contexts
        context_map = {
            "platform": PaymentContext.AD_POSTING,
            "cart": PaymentContext.PRODUCT_PURCHASE,
        }
        context = context_map.get(context, context)

        payment_config = PaymentMethodConfig.get_for_context(context)

        # First check if the method is enabled in PaymentMethodConfig
        if not payment_config.is_method_enabled(payment_method) or not payment_config.is_active:
            return False

        # Get site configuration for global payment flags
        site_config = SiteConfiguration.get_solo()

        # Check global payment settings based on payment method type
        # Online payment methods: visa, paypal, paymob
        # Note: ALLOW_ONLINE_PAYMENT lives in SiteConfiguration, not constance
        if payment_method in ["visa", "paypal", "paymob"]:
            if not site_config.allow_online_payment:
                return False
            # Additionally check if specific provider is enabled
            if payment_method == "paypal":
                try:
                    from .services.paypal_service import PayPalService
                    if not PayPalService.is_enabled():
                        return False
                except Exception:
                    return False
            elif payment_method in ["visa", "paymob"]:
                if not getattr(constance_config, "PAYMOB_ENABLED", True):
                    return False

        # Offline payment methods: instapay, wallet
        elif payment_method in ["instapay", "wallet"]:
            if not site_config.allow_offline_payment:
                return False

        return True

    except Exception:
        # Fallback
        allowed_methods = get_allowed_payment_methods(context)
        allowed_values = [method[0] for method in allowed_methods]
        return payment_method in allowed_values


def get_payment_method_display(payment_method):
    """Get display name for payment method"""
    all_methods = {
        "visa": _("بطاقة فيزا/ماستركارد"),
        "paypal": _("باي بال"),
        "wallet": _("محفظة إلكترونية"),
        "instapay": _("إنستا باي"),
        "cod": _("الدفع عند الاستلام"),
        "partial": _("دفع جزئي"),
    }
    return all_methods.get(payment_method, payment_method)


def get_cod_deposit_info(context, total_amount):
    """
    Get COD deposit information for a given context and amount.

    Args:
        context: Payment context
        total_amount: Total order amount (Decimal)

    Returns:
        dict: {
            'requires_deposit': bool,
            'deposit_amount': Decimal,
            'deposit_percentage': Decimal,
            'remaining_amount': Decimal,
        }
    """
    from decimal import Decimal

    try:
        from content.models import PaymentMethodConfig

        config = PaymentMethodConfig.get_for_context(context)

        if not config.cod_requires_deposit:
            return {
                'requires_deposit': False,
                'deposit_amount': Decimal("0.00"),
                'deposit_percentage': Decimal("0.00"),
                'remaining_amount': total_amount,
            }

        deposit_amount = config.calculate_cod_deposit(total_amount)
        remaining_amount = total_amount - deposit_amount

        return {
            'requires_deposit': True,
            'deposit_amount': deposit_amount,
            'deposit_percentage': config.cod_deposit_percentage if config.cod_deposit_type == 'percentage' else Decimal("0.00"),
            'remaining_amount': remaining_amount,
        }

    except Exception as e:
        print(f"Warning: Could not calculate COD deposit: {e}")
        # Default: 20% deposit
        deposit = (total_amount * Decimal("0.20")).quantize(Decimal("0.01"))
        return {
            'requires_deposit': True,
            'deposit_amount': deposit,
            'deposit_percentage': Decimal("20.00"),
            'remaining_amount': total_amount - deposit,
        }
