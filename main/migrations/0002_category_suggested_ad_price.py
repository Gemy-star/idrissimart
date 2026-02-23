# Generated migration for adding suggested_ad_price field to Category model

from django.core.validators import MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='suggested_ad_price',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='السعر المقترح أو النموذجي للإعلانات في هذا القسم (اختياري)',
                max_digits=10,
                null=True,
                validators=[MinValueValidator(0)],
                verbose_name='السعر المقترح للإعلان'
            ),
        ),
    ]
