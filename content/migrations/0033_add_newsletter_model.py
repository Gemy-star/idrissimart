from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0032_enable_paypal_by_default"),
    ]

    operations = [
        migrations.CreateModel(
            name="Newsletter",
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
                    "email",
                    models.EmailField(
                        db_index=True,
                        max_length=254,
                        unique=True,
                        verbose_name="البريد الإلكتروني",
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True,
                        help_text="رقم الهاتف لإرسال المحتوى عبر SMS (اختياري)",
                        max_length=20,
                        verbose_name="رقم الهاتف",
                    ),
                ),
                (
                    "receive_email",
                    models.BooleanField(
                        default=True,
                        verbose_name="استقبال عبر البريد الإلكتروني",
                    ),
                ),
                (
                    "receive_sms",
                    models.BooleanField(
                        default=False,
                        verbose_name="استقبال عبر رسائل نصية",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        verbose_name="نشط",
                    ),
                ),
                (
                    "ip_address",
                    models.GenericIPAddressField(
                        blank=True,
                        null=True,
                        verbose_name="عنوان IP",
                    ),
                ),
                (
                    "user_agent",
                    models.TextField(
                        blank=True,
                        verbose_name="معلومات المتصفح",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="تاريخ الاشتراك",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                    ),
                ),
                (
                    "last_notification_sent",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="آخر تنبيه تم إرساله",
                    ),
                ),
                (
                    "country",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="content.country",
                        verbose_name="الدولة",
                    ),
                ),
            ],
            options={
                "verbose_name": "اشتراك النشرة البريدية",
                "verbose_name_plural": "اشتراكات النشرة البريدية",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="newsletter",
            index=models.Index(
                fields=["email"],
                name="content_new_email_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="newsletter",
            index=models.Index(
                fields=["is_active"],
                name="content_new_is_active_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="newsletter",
            index=models.Index(
                fields=["created_at"],
                name="content_new_created_at_idx",
            ),
        ),
    ]
