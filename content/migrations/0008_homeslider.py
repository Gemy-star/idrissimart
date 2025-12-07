# Generated migration for HomeSlider model

from django.db import migrations, models
import django_ckeditor_5.fields


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0007_alter_contactpage_map_embed_code"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomeSlider",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(max_length=200, verbose_name="العنوان - Title"),
                ),
                (
                    "title_ar",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="العنوان بالعربية"
                    ),
                ),
                (
                    "subtitle",
                    models.TextField(
                        blank=True, verbose_name="العنوان الفرعي - Subtitle"
                    ),
                ),
                (
                    "subtitle_ar",
                    models.TextField(
                        blank=True, verbose_name="العنوان الفرعي بالعربية"
                    ),
                ),
                (
                    "description",
                    django_ckeditor_5.fields.CKEditor5Field(
                        blank=True, verbose_name="الوصف - Description"
                    ),
                ),
                (
                    "description_ar",
                    django_ckeditor_5.fields.CKEditor5Field(
                        blank=True, verbose_name="الوصف بالعربية"
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        help_text="الحجم الموصى به: 1920x800 بكسل",
                        upload_to="homepage/slider/",
                        verbose_name="الصورة - Image",
                    ),
                ),
                (
                    "button_text",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="نص الزر - Button Text"
                    ),
                ),
                (
                    "button_text_ar",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="نص الزر بالعربية"
                    ),
                ),
                (
                    "button_url",
                    models.CharField(
                        blank=True,
                        max_length=500,
                        verbose_name="رابط الزر - Button URL",
                    ),
                ),
                (
                    "background_color",
                    models.CharField(
                        default="#4B315E",
                        help_text="كود اللون hex مثل: #4B315E",
                        max_length=20,
                        verbose_name="لون الخلفية",
                    ),
                ),
                (
                    "text_color",
                    models.CharField(
                        default="#FFFFFF",
                        help_text="كود اللون hex مثل: #FFFFFF",
                        max_length=20,
                        verbose_name="لون النص",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="نشط - Active"),
                ),
                (
                    "order",
                    models.IntegerField(
                        default=0,
                        help_text="يتم عرض الشرائح حسب الترتيب التصاعدي",
                        verbose_name="الترتيب - Order",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "شريحة الصفحة الرئيسية",
                "verbose_name_plural": "شرائح الصفحة الرئيسية",
                "ordering": ["order", "-created_at"],
            },
        ),
    ]
