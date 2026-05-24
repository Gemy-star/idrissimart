from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "1021_add_coupon_model_and_order_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="paidbanner",
            name="target_pages",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="اختر الصفحات التي سيظهر عليها الإعلان. إذا تُركت فارغة يظهر الإعلان في كل الصفحات",
                verbose_name="الصفحات المستهدفة - Target Pages",
            ),
        ),
    ]
