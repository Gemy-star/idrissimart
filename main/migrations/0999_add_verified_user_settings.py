# Generated migration for verified user settings

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0048_add_is_paid_to_classifiedad'),
    ]

    operations = [
        # Advanced notification preferences for verified users
        migrations.AddField(
            model_name='user',
            name='notify_new_messages',
            field=models.BooleanField(
                default=True,
                verbose_name='إشعار بالرسائل الجديدة'
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='notify_ad_views',
            field=models.BooleanField(
                default=False,
                verbose_name='إحصائيات المشاهدات'
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='notify_price_alerts',
            field=models.BooleanField(
                default=False,
                verbose_name='تنبيهات الأسعار'
            ),
        ),
        
        # Auto-publish settings for verified users
        migrations.AddField(
            model_name='user',
            name='auto_renew_ads',
            field=models.BooleanField(
                default=False,
                verbose_name='تجديد تلقائي للإعلانات'
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='auto_boost_ads',
            field=models.BooleanField(
                default=False,
                verbose_name='ترويج تلقائي'
            ),
        ),
        
        # Analytics settings for verified users
        migrations.AddField(
            model_name='user',
            name='enable_analytics',
            field=models.BooleanField(
                default=True,
                verbose_name='تفعيل التحليلات المتقدمة'
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='weekly_reports',
            field=models.BooleanField(
                default=False,
                verbose_name='تقارير أسبوعية'
            ),
        ),
        
        # Additional analytics fields
        migrations.AddField(
            model_name='user',
            name='total_ad_views',
            field=models.IntegerField(
                default=0,
                verbose_name='إجمالي المشاهدات'
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='engagement_rate',
            field=models.DecimalField(
                max_digits=5,
                decimal_places=2,
                default=0,
                verbose_name='معدل التفاعل'
            ),
        ),
    ]
