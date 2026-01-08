# Generated manually for adding country field to Order model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0041_update_adreview_approval_default'),
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='country',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='orders',
                to='content.country',
                verbose_name='الدولة'
            ),
        ),
    ]
