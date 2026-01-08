# Generated manually - Tell Django that country_id is a ForeignKey
# No database changes needed, just update Django's state
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0026_alter_paymentmethodconfig_cod_requires_deposit"),
        ("main", "0044_convert_user_country_to_fk"),
    ]

    operations = [
        # Use SeparateDatabaseAndState because country_id column already exists
        # We just need to tell Django it's a ForeignKey
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name="user",
                    name="country",
                    field=models.ForeignKey(
                        blank=True,
                        db_column="country_id",  # Use existing column
                        help_text="الدولة التي اختارها المستخدم عند التسجيل",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="users",
                        to="content.country",
                        verbose_name="الدولة - Country",
                        db_constraint=False,  # Don't create DB constraint - MariaDB issues
                    ),
                ),
            ],
            # No database operations - column already exists
            database_operations=[],
        ),
    ]
