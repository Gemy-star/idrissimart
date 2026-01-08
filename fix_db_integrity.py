import sqlite3
import os

# Configuration
DB_FILES = ["db.sqlite", "db.sqlite3"]
TABLE_USER = "users"
TABLE_COUNTRY = "content_country"


def get_db_path():
    # Check current directory for database files
    for f in DB_FILES:
        if os.path.exists(f):
            return f
    return None


def fix_integrity():
    db_path = get_db_path()
    if not db_path:
        print("❌ Database file not found (looked for db.sqlite, db.sqlite3).")
        return

    print(f"📂 Opening database: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # 1. Identify the column in users table
        cursor.execute(f"PRAGMA table_info({TABLE_USER})")
        user_columns = [row["name"] for row in cursor.fetchall()]

        target_column = "country_id"
        if "country_id" in user_columns:
            target_column = "country_id"
        elif "country" in user_columns:
            target_column = "country"
        else:
            print(
                f"⚠️ Column 'country_id' or 'country' not found in table '{TABLE_USER}'."
            )
            return

        print(f"✓ Found column: {target_column}")

        # 2. Check content_country schema to find PK
        cursor.execute(f"PRAGMA table_info({TABLE_COUNTRY})")
        country_cols_info = cursor.fetchall()
        country_cols = [row["name"] for row in country_cols_info]

        # Find PK column (usually 'id')
        pk_col = "id"
        for row in country_cols_info:
            if row["pk"] == 1:
                pk_col = row["name"]
                break

        print(f"✓ {TABLE_COUNTRY} PK column: {pk_col}")

        # 3. Find all users with invalid or empty country_id
        cursor.execute(f"SELECT id, {target_column} FROM {TABLE_USER}")
        all_users = cursor.fetchall()

        # Get all valid country IDs
        cursor.execute(f"SELECT {pk_col} FROM {TABLE_COUNTRY}")
        valid_country_ids = [row[pk_col] for row in cursor.fetchall()]

        print(f"✓ Found {len(valid_country_ids)} valid countries")

        # Find users with invalid country_id
        invalid_users = []
        for user in all_users:
            country_id = user[target_column]
            # Check if empty string, None, or not in valid IDs
            if (
                not country_id
                or country_id == ""
                or country_id not in valid_country_ids
            ):
                invalid_users.append((user["id"], country_id))

        if not invalid_users:
            print("✅ All users have valid country_id. No fix needed.")
            return

        print(f"❌ Found {len(invalid_users)} users with invalid country_id:")
        for user_id, country_id in invalid_users:
            print(f"   - User ID {user_id}: country_id = '{country_id}'")

        # 4. Get or create a default country
        default_country_id = None

        if valid_country_ids:
            # Use first valid country
            default_country_id = valid_country_ids[0]
            print(f"✓ Will use existing country ID: {default_country_id}")
        else:
            # Insert a default country
            print(f"🛠️ No countries exist. Inserting default country...")
            try:
                insert_data = {}

                # Force integer ID if PK is 'id'
                if pk_col == "id":
                    insert_data["id"] = 1
                if "code" in country_cols:
                    insert_data["code"] = "SA"
                if "name" in country_cols:
                    insert_data["name"] = "Saudi Arabia"
                if "name_ar" in country_cols:
                    insert_data["name_ar"] = "السعودية"
                if "name_en" in country_cols:
                    insert_data["name_en"] = "Saudi Arabia"
                if "currency" in country_cols:
                    insert_data["currency"] = "SAR"
                if "phone_code" in country_cols:
                    insert_data["phone_code"] = "+966"
                if "is_active" in country_cols:
                    insert_data["is_active"] = 1

                cols_str = ", ".join([f'"{k}"' for k in insert_data.keys()])
                placeholders = ", ".join(["?"] * len(insert_data))
                values = tuple(insert_data.values())

                cursor.execute(
                    f"INSERT INTO {TABLE_COUNTRY} ({cols_str}) VALUES ({placeholders})",
                    values,
                )
                conn.commit()
                default_country_id = insert_data.get(pk_col, 1)
                print(f"✅ Inserted default country with ID: {default_country_id}")

            except Exception as insert_e:
                print(f"❌ Failed to insert country: {insert_e}")
                return

        # 5. Update all invalid users
        print(
            f"\n🔄 Updating {len(invalid_users)} users to country ID {default_country_id}..."
        )
        updated_count = 0

        for user_id, old_country_id in invalid_users:
            try:
                cursor.execute(
                    f"UPDATE {TABLE_USER} SET {target_column}=? WHERE id=?",
                    (default_country_id, user_id),
                )
                updated_count += 1
            except Exception as update_e:
                print(f"   ❌ Failed to update user {user_id}: {update_e}")

        conn.commit()
        print(f"✅ Successfully updated {updated_count} users!")

        # 6. Verify the fix
        print("\n🔍 Verifying fix...")
        cursor.execute(f"SELECT id, {target_column} FROM {TABLE_USER}")
        all_users_after = cursor.fetchall()

        still_invalid = []
        for user in all_users_after:
            country_id = user[target_column]
            if (
                not country_id
                or country_id == ""
                or country_id not in [default_country_id] + valid_country_ids
            ):
                still_invalid.append((user["id"], country_id))

        if still_invalid:
            print(
                f"⚠️ Warning: {len(still_invalid)} users still have invalid country_id:"
            )
            for user_id, country_id in still_invalid:
                print(f"   - User ID {user_id}: country_id = '{country_id}'")
        else:
            print("✅ All users now have valid country_id!")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        import traceback

        traceback.print_exc()
    finally:
        conn.close()


if __name__ == "__main__":
    fix_integrity()
