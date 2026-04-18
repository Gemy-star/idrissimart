# Generated manually to rename PaidAdvertisement to PaidBanner

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '1007_add_advertising_space_field'),
    ]

    operations = [
        # Rename the database table
        migrations.AlterModelTable(
            name='paidadvertisement',
            table='paid_banners',
        ),

        # Rename the model
        migrations.RenameModel(
            old_name='PaidAdvertisement',
            new_name='PaidBanner',
        ),

        # Update the Meta options
        migrations.AlterModelOptions(
            name='paidbanner',
            options={
                'ordering': ['-priority', 'order', '-created_at'],
                'verbose_name': 'بنر مدفوع - Paid Banner',
                'verbose_name_plural': 'البنرات المدفوعة - Paid Banners',
            },
        ),
    ]
