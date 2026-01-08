# Generated manually for PaymentMethodConfig model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethodConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('context', models.CharField(choices=[('ad_posting', 'نشر الإعلان'), ('ad_upgrade', 'ترقية الإعلان'), ('package_purchase', 'شراء باقة'), ('product_purchase', 'شراء منتج من السلة')], max_length=50, unique=True, verbose_name='سياق الدفع')),
                ('visa_enabled', models.BooleanField(default=True, verbose_name='فيزا/ماستركارد')),
                ('paypal_enabled', models.BooleanField(default=False, verbose_name='باي بال')),
                ('wallet_enabled', models.BooleanField(default=True, verbose_name='محفظة إلكترونية')),
                ('instapay_enabled', models.BooleanField(default=True, verbose_name='إنستا باي')),
                ('cod_enabled', models.BooleanField(default=False, verbose_name='الدفع عند الاستلام')),
                ('partial_enabled', models.BooleanField(default=False, verbose_name='دفع جزئي')),
                ('cod_requires_deposit', models.BooleanField(default=True, help_text='إذا كان مفعلاً, يجب دفع مبلغ الحجز قبل تأكيد الطلب', verbose_name='يتطلب الدفع عند الاستلام مبلغ حجز')),
                ('cod_deposit_type', models.CharField(choices=[('fixed', 'مبلغ ثابت'), ('percentage', 'نسبة مئوية')], default='percentage', max_length=20, verbose_name='نوع مبلغ الحجز')),
                ('cod_deposit_amount', models.DecimalField(decimal_places=2, default=0, help_text="يستخدم إذا كان النوع 'مبلغ ثابت'", max_digits=10, verbose_name='مبلغ الحجز الثابت')),
                ('cod_deposit_percentage', models.DecimalField(decimal_places=2, default=20.0, help_text="يستخدم إذا كان النوع 'نسبة مئوية' (مثال: 20 = 20%)", max_digits=5, verbose_name='نسبة مبلغ الحجز %')),
                ('notes', models.TextField(blank=True, help_text='ملاحظات إضافية حول هذا السياق', verbose_name='ملاحظات')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
            ],
            options={
                'verbose_name': 'إعدادات وسائل الدفع',
                'verbose_name_plural': 'إعدادات وسائل الدفع',
                'ordering': ['context'],
            },
        ),
    ]
