# Generated manually to convert User.country from CharField to ForeignKey
import django.db.models.deletion
from django.db import migrations, models


def column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = %s
          AND column_name = %s
    """,
        [table_name, column_name],
    )
    return cursor.fetchone()[0] > 0


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
        # Check if old 'country' CharField exists
        has_old_country = column_exists(cursor, "users", "country")

        if has_old_country:
            print("ℹ️  Found old 'country' CharField column, will migrate data...")
            # Rename old column first
            try:
                cursor.execute(
                    "ALTER TABLE users CHANGE COLUMN country country_old VARCHAR(100)"
                )
                print("✅ Renamed old country column to country_old")
            except Exception as e:
                print(f"⚠️  Error renaming country column: {e}")
        else:
            print("ℹ️  No old 'country' CharField column found, skipping rename...")

        # Create temporary column for the new FK if it doesn't exist
        if not column_exists(cursor, "users", "country_id"):
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN country_id BIGINT NULL")
                print("✅ Created country_id column")
            except Exception as e:
                print(f"ℹ️  Column country_id might already exist: {e}")

        # Set all users to the default country
        cursor.execute(
            f"""
            UPDATE users
            SET country_id = {default_country.id}
            WHERE country_id IS NULL
        """
        )

        # Drop old column if it exists
        if has_old_country:
            try:
                cursor.execute("ALTER TABLE users DROP COLUMN country_old")
                print("✅ Dropped old country_old column")
            except Exception as e:
                print(f"⚠️  Error dropping country_old: {e}")

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
        # Step 1: Run data migration - handles everything with raw SQL
        migrations.RunPython(migrate_country_data, reverse_migration),
        # Step 2: Add FK constraint to existing country_id column
        migrations.RunSQL(
            sql="""
                ALTER TABLE users
                ADD CONSTRAINT users_country_id_fk
                FOREIGN KEY (country_id)
                REFERENCES content_country(id)
                ON DELETE SET NULL
            """,
            reverse_sql="ALTER TABLE users DROP FOREIGN KEY users_country_id_fk",
        ),
        # Step 3: Update city field help text
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
