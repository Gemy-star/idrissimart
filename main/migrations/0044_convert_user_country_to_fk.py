# Generated manually to convert User.country from CharField to ForeignKey
import django.db.models.deletion
from django.db import migrations, models


def get_table_info(cursor, table_name, column_name):
    """Get detailed column information"""
    cursor.execute(
        """
        SELECT COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = %s
          AND column_name = %s
    """,
        [table_name, column_name],
    )
    result = cursor.fetchone()
    return result if result else None


def get_table_engine(cursor, table_name):
    """Get table storage engine"""
    cursor.execute(
        """
        SELECT ENGINE
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
          AND table_name = %s
    """,
        [table_name],
    )
    result = cursor.fetchone()
    return result[0] if result else None


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
                # Use BIGINT UNSIGNED to match the content_country.id type
                cursor.execute(
                    "ALTER TABLE users ADD COLUMN country_id BIGINT UNSIGNED NULL"
                )
                print("✅ Created country_id column (BIGINT UNSIGNED)")
            except Exception as e:
                print(f"ℹ️  Column country_id might already exist: {e}")
        else:
            # If column exists, make sure it's the correct type
            try:
                cursor.execute(
                    "ALTER TABLE users MODIFY COLUMN country_id BIGINT UNSIGNED NULL"
                )
                print("✅ Modified country_id to BIGINT UNSIGNED")
            except Exception as e:
                print(f"⚠️  Could not modify country_id type: {e}")

        # Set all users to the default country
        cursor.execute(
            f"""
            UPDATE users
            SET country_id = {default_country.id}
            WHERE country_id IS NULL
        """
        )

        # Also fix any invalid country_id values (e.g., pointing to non-existent countries)
        cursor.execute(
            f"""
            UPDATE users
            SET country_id = {default_country.id}
            WHERE country_id NOT IN (SELECT id FROM content_country WHERE is_active = 1)
        """
        )

        # Debug: Check table structures before adding FK
        print("\n🔍 Debugging FK constraint issue:")

        # Check users table engine
        users_engine = get_table_engine(cursor, "users")
        country_engine = get_table_engine(cursor, "content_country")
        print(f"  users table engine: {users_engine}")
        print(f"  content_country table engine: {country_engine}")

        # Check column types
        users_country_info = get_table_info(cursor, "users", "country_id")
        country_id_info = get_table_info(cursor, "content_country", "id")
        print(f"  users.country_id type: {users_country_info}")
        print(f"  content_country.id type: {country_id_info}")

        # Ensure both tables use InnoDB
        if users_engine != "InnoDB":
            print(f"  ⚠️  Converting users table to InnoDB...")
            cursor.execute("ALTER TABLE users ENGINE=InnoDB")
            print(f"  ✅ Converted users to InnoDB")

        if country_engine != "InnoDB":
            print(f"  ⚠️  Converting content_country table to InnoDB...")
            cursor.execute("ALTER TABLE content_country ENGINE=InnoDB")
            print(f"  ✅ Converted content_country to InnoDB")
        print()

        # Verify all users have valid country_id
        cursor.execute(
            """
            SELECT COUNT(*) FROM users
            WHERE country_id IS NULL
               OR country_id NOT IN (SELECT id FROM content_country WHERE is_active = 1)
        """
        )
        invalid_count = cursor.fetchone()[0]
        if invalid_count > 0:
            print(f"⚠️  Warning: {invalid_count} users still have invalid country_id!")
        else:
            print("✅ All users have valid country_id values")

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
        # Step 2: Add FK constraint using raw SQL with proper error handling
        migrations.RunSQL(
            sql="""
                ALTER TABLE users
                ADD CONSTRAINT users_country_id_fk
                FOREIGN KEY (country_id)
                REFERENCES content_country(id)
                ON DELETE SET NULL
            """,
            reverse_sql="ALTER TABLE users DROP FOREIGN KEY users_country_id_fk",
            state_operations=[
                # Tell Django that country is now a ForeignKey
                migrations.AlterField(
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
                        db_column="country_id",
                    ),
                ),
            ],
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
