from django.db import migrations, models


def enable_paypal_on_existing_configs(apps, schema_editor):
    PaymentMethodConfig = apps.get_model("content", "PaymentMethodConfig")
    PaymentMethodConfig.objects.filter(paypal_enabled=False).update(paypal_enabled=True)


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0031_add_auto_refresh_and_video_pricing"),
    ]

    operations = [
        migrations.AlterField(
            model_name="paymentmethodconfig",
            name="paypal_enabled",
            field=models.BooleanField(default=True, verbose_name="باي بال"),
        ),
        migrations.RunPython(
            enable_paypal_on_existing_configs,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
