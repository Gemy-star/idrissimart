# Generated manually to populate default payment method configurations

from django.db import migrations


def create_default_configs(apps, schema_editor):
    """Create default payment method configurations"""
    PaymentMethodConfig = apps.get_model('content', 'PaymentMethodConfig')
    
    # Ad Posting - Online methods only
    PaymentMethodConfig.objects.get_or_create(
        context='ad_posting',
        defaults={
            'visa_enabled': True,
            'paypal_enabled': False,
            'wallet_enabled': True,
            'instapay_enabled': True,
            'cod_enabled': False,
            'partial_enabled': False,
            'notes': 'نشر الإعلان - وسائل الدفع الإلكتروني فقط',
            'is_active': True,
        }
    )
    
    # Ad Upgrade - Online methods only
    PaymentMethodConfig.objects.get_or_create(
        context='ad_upgrade',
        defaults={
            'visa_enabled': True,
            'paypal_enabled': False,
            'wallet_enabled': True,
            'instapay_enabled': True,
            'cod_enabled': False,
            'partial_enabled': False,
            'notes': 'ترقية الإعلان - وسائل الدفع الإلكتروني فقط',
            'is_active': True,
        }
    )
    
    # Package Purchase - Online methods only
    PaymentMethodConfig.objects.get_or_create(
        context='package_purchase',
        defaults={
            'visa_enabled': True,
            'paypal_enabled': False,
            'wallet_enabled': True,
            'instapay_enabled': True,
            'cod_enabled': False,
            'partial_enabled': False,
            'notes': 'شراء الباقات - وسائل الدفع الإلكتروني فقط',
            'is_active': True,
        }
    )
    
    # Product Purchase - All methods including COD
    PaymentMethodConfig.objects.get_or_create(
        context='product_purchase',
        defaults={
            'visa_enabled': True,
            'paypal_enabled': False,
            'wallet_enabled': True,
            'instapay_enabled': True,
            'cod_enabled': True,
            'partial_enabled': True,
            'cod_requires_deposit': True,
            'cod_deposit_type': 'percentage',
            'cod_deposit_percentage': 20.00,
            'notes': 'شراء المنتجات - جميع وسائل الدفع متاحة بما فيها الدفع عند الاستلام',
            'is_active': True,
        }
    )


def reverse_func(apps, schema_editor):
    """Remove all payment method configurations"""
    PaymentMethodConfig = apps.get_model('content', 'PaymentMethodConfig')
    PaymentMethodConfig.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0002_paymentmethodconfig'),
    ]

    operations = [
        migrations.RunPython(create_default_configs, reverse_func),
    ]
