from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0048_add_is_paid_to_classifiedad"),
        ("main", "1002_add_auto_refresh_and_video_pricing"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="payment_method",
            field=models.CharField(
                choices=[
                    ("cod", "الدفع عند الاستلام"),
                    ("online", "الدفع الإلكتروني - Paymob"),
                    ("paypal", "باي بال - PayPal"),
                    ("instapay", "InstaPay"),
                    ("wallet", "محفظة إلكترونية"),
                    ("partial", "دفع جزئي"),
                ],
                default="cod",
                max_length=20,
                verbose_name="طريقة الدفع",
            ),
        ),
    ]
