"""
Database Integrity Fix Script for Country Foreign Key
Works with both SQLite (local) and MySQL (production)
Uses Django ORM for database operations
"""

import os
import sys
import django

# Setup Django environment
if "DJANGO_SETTINGS_MODULE" not in os.environ:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings.docker")

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize Django
django.setup()

from django.db import connection, transaction
from django.contrib.auth import get_user_model
from content.models import Country

User = get_user_model()


def fix_country_integrity():
    """
    Fix users with invalid country_id values
    - Finds users with non-existent or invalid country references
    - Updates them to use a valid default country
    """

    print("=" * 60)
    print("🔧 Database Integrity Fix - Country Foreign Key")
    print("=" * 60)
    print(f"📊 Database: {connection.settings_dict.get('NAME', 'Unknown')}")
    print(f"🔌 Engine: {connection.settings_dict.get('ENGINE', 'Unknown')}")
    print()

    try:
        # Step 1: Get all valid countries
        valid_countries = list(
            Country.objects.filter(is_active=True).values_list("id", flat=True)
        )

        if not valid_countries:
            print("❌ No active countries found in database!")
            print("⚠️  Please create at least one country before running migrations.")
            return False

        print(f"✓ Found {len(valid_countries)} active countries")
        print(
            f"  Valid IDs: {valid_countries[:5]}{'...' if len(valid_countries) > 5 else ''}"
        )
        print()

        # Step 2: Find users with invalid country_id using raw SQL
        # This is necessary because Django ORM might fail with invalid FK values
        with connection.cursor() as cursor:
            # Get table name
            user_table = User._meta.db_table
            print(f"📋 User table name: {user_table}")

            # Get database engine
            engine = connection.settings_dict.get("ENGINE", "")
            is_mysql = "mysql" in engine.lower()
            print(f"🔍 Database type: {'MySQL' if is_mysql else 'SQLite'}")
            print()

            # Build query based on database type
            if is_mysql:
                # MySQL: Handle string values like 'SA' that can't be cast to INT
                query = f"""
                    SELECT u.id, u.country_id
                    FROM {user_table} u
                    WHERE u.country_id IS NULL
                       OR u.country_id = ''
                       OR NOT EXISTS (
                           SELECT 1 FROM content_country c
                           WHERE c.id = u.country_id AND c.is_active = 1
                       )
                       OR u.country_id REGEXP '^[^0-9]'
                """
            else:
                # SQLite: Simpler query
                query = f"""
                    SELECT id, country_id
                    FROM {user_table}
                    WHERE country_id IS NULL
                       OR country_id = ''
                       OR country_id NOT IN (
                           SELECT id FROM content_country WHERE is_active = 1
                       )
                """

            # Find users with invalid country_id
            try:
                cursor.execute(query)
                invalid_users = cursor.fetchall()
            except Exception as query_error:
                print(f"⚠️  Query error: {query_error}")
                print("   Trying alternative approach...")

                # Fallback: Get all users and check in Python
                cursor.execute(f"SELECT id, country_id FROM {user_table}")
                all_users = cursor.fetchall()

                invalid_users = []
                for user_id, country_id in all_users:
                    # Check if invalid
                    if (
                        not country_id
                        or str(country_id).strip() == ""
                        or not str(country_id).isdigit()
                        or int(country_id) not in valid_countries
                    ):
                        invalid_users.append((user_id, country_id))

        if not invalid_users:
            print("✅ All users have valid country references!")
            print("   No fixes needed.")
            return True

        print(f"❌ Found {len(invalid_users)} users with invalid country_id:")

        # Show sample of invalid users
        sample_size = min(10, len(invalid_users))
        for user_id, country_id in invalid_users[:sample_size]:
            print(f"   - User ID {user_id}: country_id = '{country_id}'")
        if len(invalid_users) > sample_size:
            print(f"   ... and {len(invalid_users) - sample_size} more")
        print()

        # Step 3: Get default country (first active country)
        default_country = Country.objects.filter(is_active=True).order_by("id").first()

        if not default_country:
            print("❌ Could not find a default country to use!")
            return False

        print(f"✓ Default country selected:")
        print(f"  ID: {default_country.id}")
        print(f"  Name: {default_country.name} / {default_country.name_en}")
        print()

        # Step 4: Update invalid users
        print(
            f"🔄 Updating {len(invalid_users)} users to country ID {default_country.id}..."
        )

        updated_count = 0
        failed_count = 0

        with transaction.atomic():
            for user_id, old_country_id in invalid_users:
                try:
                    # Use raw SQL to update to avoid Django FK validation
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"UPDATE {user_table} SET country_id = %s WHERE id = %s",
                            [default_country.id, user_id],
                        )
                    updated_count += 1
                except Exception as e:
                    failed_count += 1
                    print(f"   ❌ Failed to update user {user_id}: {e}")

        print(f"✅ Successfully updated {updated_count} users!")
        if failed_count > 0:
            print(f"⚠️  Failed to update {failed_count} users")
        print()

        # Step 5: Verify the fix
        print("🔍 Verifying fix...")

        with connection.cursor() as cursor:
            # Use database-specific verification query
            if is_mysql:
                verify_query = f"""
                    SELECT COUNT(*)
                    FROM {user_table} u
                    WHERE u.country_id IS NULL
                       OR u.country_id = ''
                       OR NOT EXISTS (
                           SELECT 1 FROM content_country c
                           WHERE c.id = u.country_id AND c.is_active = 1
                       )
                       OR u.country_id REGEXP '^[^0-9]'
                """
            else:
                verify_query = f"""
                    SELECT COUNT(*)
                    FROM {user_table}
                    WHERE country_id IS NULL
                       OR country_id = ''
                       OR country_id NOT IN (
                           SELECT id FROM content_country WHERE is_active = 1
                       )
                """

            cursor.execute(verify_query)
            remaining_invalid = cursor.fetchone()[0]

        if remaining_invalid > 0:
            print(
                f"⚠️  Warning: {remaining_invalid} users still have invalid country_id"
            )
            return False
        else:
            print("✅ All users now have valid country references!")
            print()
            print("=" * 60)
            print("✅ Database integrity fix completed successfully!")
            print("=" * 60)
            return True

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = fix_country_integrity()
    sys.exit(0 if success else 1)
