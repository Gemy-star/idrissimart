# Generated manually for adding AboutPage sections and dynamic content
from django.db import migrations, models
import django.db.models.deletion
from django_ckeditor_5.fields import CKEditor5Field


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0023_merge_20260109_0017'),
    ]

    operations = [
        # Add new fields to AboutPage
        migrations.AddField(
            model_name='aboutpage',
            name='tagline',
            field=models.CharField(
                default='منصة تجمع سوق واحد',
                help_text='العنوان الأول الذي يظهر أسفل العنوان الرئيسي',
                max_length=200,
                verbose_name='الشعار - Tagline'
            ),
        ),
        migrations.AddField(
            model_name='aboutpage',
            name='tagline_ar',
            field=models.CharField(
                default='منصة تجمع سوق واحد',
                max_length=200,
                verbose_name='الشعار بالعربية'
            ),
        ),
        migrations.AddField(
            model_name='aboutpage',
            name='subtitle',
            field=models.TextField(
                blank=True,
                default='متخصص يستفيد منه المتخصصون والجمهور العام الذي يحتاج إلى أي من خدمات هذا السوق',
                verbose_name='العنوان الفرعي - Subtitle'
            ),
        ),
        migrations.AddField(
            model_name='aboutpage',
            name='subtitle_ar',
            field=models.TextField(
                blank=True,
                default='متخصص يستفيد منه المتخصصون والجمهور العام الذي يحتاج إلى أي من خدمات هذا السوق',
                verbose_name='العنوان الفرعي بالعربية'
            ),
        ),
        migrations.AddField(
            model_name='aboutpage',
            name='what_we_offer_title',
            field=models.CharField(
                default='ماذا نقدم؟',
                max_length=200,
                verbose_name='عنوان قسم ماذا نقدم - What We Offer Title'
            ),
        ),
        migrations.AddField(
            model_name='aboutpage',
            name='what_we_offer_title_ar',
            field=models.CharField(
                default='ماذا نقدم؟',
                max_length=200,
                verbose_name='عنوان قسم ماذا نقدم بالعربية'
            ),
        ),

        # Create AboutPageSection model
        migrations.CreateModel(
            name='AboutPageSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tab_title', models.CharField(
                    help_text='العنوان الذي يظهر في زر التبويب (مثل: للأفراد، للشركات)',
                    max_length=100,
                    verbose_name='عنوان التبويب - Tab Title'
                )),
                ('tab_title_ar', models.CharField(
                    max_length=100,
                    verbose_name='عنوان التبويب بالعربية'
                )),
                ('icon', models.CharField(
                    blank=True,
                    help_text='أيقونة إيموجي أو رمز (مثل: 📢، 🛒، 🔧)',
                    max_length=50,
                    verbose_name='الأيقونة - Icon'
                )),
                ('content', CKEditor5Field(
                    blank=True,
                    help_text='محتوى القسم بتنسيق HTML',
                    verbose_name='المحتوى - Content',
                    config_name='default'
                )),
                ('content_ar', CKEditor5Field(
                    blank=True,
                    verbose_name='المحتوى بالعربية',
                    config_name='default'
                )),
                ('order', models.IntegerField(
                    default=0,
                    help_text='ترتيب ظهور التبويب',
                    verbose_name='الترتيب - Order'
                )),
                ('is_active', models.BooleanField(
                    default=True,
                    verbose_name='نشط - Active'
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('about_page', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='sections',
                    to='content.aboutpage',
                    verbose_name='صفحة من نحن'
                )),
            ],
            options={
                'verbose_name': 'قسم من نحن - ماذا نقدم',
                'verbose_name_plural': 'أقسام من نحن - ماذا نقدم',
                'ordering': ['order', 'id'],
            },
        ),
    ]
