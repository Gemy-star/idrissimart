# Generated manually to convert User.country from CharField to ForeignKey
import django.db.models.deletion
from django.db import migrations, models


def migrate_country_data(apps, schema_editor):
    """
    Migrate existing country CharField values to ForeignKey IDs
    This is a data migration that should run BEFORE altering the field
    """
    User = apps.get_model("main", "User")
    Country = apps.get_model("content", "Country")

    # Get the default country (first active country)
    try:
        default_country = Country.objects.filter(is_active=True).order_by("id").first()
        if not default_country:
            print("⚠️  No active countries found. Creating default country...")
            default_country = Country.objects.create(
                name="السعودية",
                name_en="Saudi Arabia",
                code="SA",
                flag_emoji="🇸🇦",
                phone_code="+966",
                currency="SAR",
                is_active=True,
                order=1,
            )
    except Exception as e:
        print(f"⚠️  Error getting default country: {e}")
        return

    # Update all users with the default country
    # Note: We'll use raw SQL to avoid FK constraint issues
    from django.db import connection

    with connection.cursor() as cursor:
        # First, create a temporary column for the new FK
        try:
            cursor.execute(
                """
                ALTER TABLE users
                ADD COLUMN country_id_new BIGINT NULL
            """
            )
        except Exception as e:
            print(f"ℹ️  Column country_id_new might already exist: {e}")

        # Set all users to the default country
        cursor.execute(
            f"""
            UPDATE users
            SET country_id_new = {default_country.id}
            WHERE country_id_new IS NULL
        """
        )

        print(f"✅ Migrated user country data to FK (Country ID: {default_country.id})")


def reverse_migration(apps, schema_editor):
    """
    Reverse the migration by converting back to CharField
    """
    from django.db import connection

    with connection.cursor() as cursor:
        # Drop the temporary column if reverting
        try:
            cursor.execute("ALTER TABLE users DROP COLUMN country_id_new")
        except Exception as e:
            print(f"ℹ️  Error dropping column: {e}")


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0026_alter_paymentmethodconfig_cod_requires_deposit"),
        ("main", "0043_add_currency_to_order"),
    ]

    operations = [
        # Step 1: Run data migration FIRST
        migrations.RunPython(migrate_country_data, reverse_migration),
        # Step 2: Rename old CharField column
        migrations.RenameField(
            model_name="user",
            old_name="country",
            new_name="country_old",
        ),
        # Step 3: Rename temporary FK column to 'country_id'
        migrations.RunSQL(
            sql="ALTER TABLE users CHANGE COLUMN country_id_new country_id BIGINT NULL",
            reverse_sql="ALTER TABLE users CHANGE COLUMN country_id country_id_new BIGINT NULL",
        ),
        # Step 4: Add the FK constraint
        migrations.AddField(
            model_name="user",
            name="country",
            field=models.ForeignKey(
                blank=True,
                help_text="الدولة التي اختارها المستخدم عند التسجيل",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="users",
                to="content.country",
                verbose_name="الدولة - Country",
                db_column="country_id",  # Use existing country_id column
            ),
        ),
        # Step 5: Remove old CharField column
        migrations.RemoveField(
            model_name="user",
            name="country_old",
        ),
        # Step 6: Update city field help text
        migrations.AlterField(
            model_name="user",
            name="city",
            field=models.CharField(
                blank=True,
                help_text="يجب اختيار المدينة من القائمة المتاحة للدولة",
                max_length=100,
                verbose_name="المدينة - City",
            ),
        ),
    ]
