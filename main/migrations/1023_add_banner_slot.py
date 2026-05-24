from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "1022_paidbanner_target_pages"),
    ]

    operations = [
        migrations.CreateModel(
            name="BannerSlot",
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
                ("name", models.CharField(max_length=120, verbose_name="اسم المساحة")),
                (
                    "name_ar",
                    models.CharField(
                        blank=True, max_length=120, verbose_name="الاسم بالعربية"
                    ),
                ),
                (
                    "slot_key",
                    models.CharField(
                        db_index=True,
                        help_text="يجب أن يطابق حقل 'المساحة الإعلانية' في الإعلانات المرتبطة بهذا السلوت",
                        max_length=100,
                        unique=True,
                        verbose_name="مفتاح المساحة",
                    ),
                ),
                (
                    "ad_type",
                    models.CharField(
                        choices=[
                            ("banner", "بانر إعلاني (728×90)"),
                            ("sidebar", "إعلان جانبي (300×250)"),
                            ("featured_box", "صندوق مميز (970×250)"),
                        ],
                        default="banner",
                        max_length=20,
                        verbose_name="نوع البانر",
                    ),
                ),
                (
                    "max_capacity",
                    models.PositiveSmallIntegerField(
                        default=3,
                        help_text="أقصى عدد من المعلنين يمكن أن يحجزوا هذا السلوت في نفس الوقت",
                        verbose_name="الحد الأقصى للمعلنين",
                    ),
                ),
                (
                    "rotation_seconds",
                    models.PositiveSmallIntegerField(
                        default=5,
                        help_text="عدد الثواني قبل التبديل إلى البانر التالي",
                        verbose_name="مدة عرض كل بانر (ثانية)",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="نشط")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "مساحة بانر (سلوت)",
                "verbose_name_plural": "مساحات البانر (سلوتس)",
                "db_table": "banner_slots",
                "ordering": ["ad_type", "name"],
            },
        ),
    ]
