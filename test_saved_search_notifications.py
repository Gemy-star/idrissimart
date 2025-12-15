"""
Test script to check SavedSearch email_notifications field behavior
Run with: python manage.py shell < test_saved_search_notifications.py
"""

from main.models import SavedSearch, User

print("=== Testing SavedSearch email_notifications field ===\n")

# Get first saved search
search = SavedSearch.objects.first()
if not search:
    print("❌ No saved searches found in database")
    print("Please create a saved search first")
else:
    print(f"✓ Found saved search: {search.name}")
    print(f"  User: {search.user.username}")
    print(f"  Current email_notifications value: {search.email_notifications}")
    print(f"  Type: {type(search.email_notifications)}")

    # Test 1: Try to set to False
    print("\n--- Test 1: Setting email_notifications to False ---")
    search.email_notifications = False
    search.save(update_fields=["email_notifications"])
    print(f"  Saved as False, reloading from DB...")

    search.refresh_from_db()
    print(f"  Value after reload: {search.email_notifications}")
    print(f"  ✓ PASS" if search.email_notifications == False else f"  ✗ FAIL")

    # Test 2: Try to set to True
    print("\n--- Test 2: Setting email_notifications to True ---")
    search.email_notifications = True
    search.save(update_fields=["email_notifications"])
    print(f"  Saved as True, reloading from DB...")

    search.refresh_from_db()
    print(f"  Value after reload: {search.email_notifications}")
    print(f"  ✓ PASS" if search.email_notifications == True else f"  ✗ FAIL")

    # Test 3: Check POST data simulation
    print("\n--- Test 3: Simulating POST request behavior ---")

    # When checkbox is checked and submitted
    post_data_checked = {"search_id": str(search.pk), "email_notifications": "on"}
    result_checked = "email_notifications" in post_data_checked
    print(
        f"  When checkbox IS checked: 'email_notifications' in POST = {result_checked}"
    )

    # When checkbox is unchecked and submitted
    post_data_unchecked = {"search_id": str(search.pk)}
    result_unchecked = "email_notifications" in post_data_unchecked
    print(
        f"  When checkbox is NOT checked: 'email_notifications' in POST = {result_unchecked}"
    )

    print("\n=== Test Complete ===")

    # Check if there are any signals that might be interfering
    print("\n--- Checking for signals ---")
    from django.db.models import signals

    print(
        f"  Pre-save signals on SavedSearch: {signals.pre_save.has_listeners(SavedSearch)}"
    )
    print(
        f"  Post-save signals on SavedSearch: {signals.post_save.has_listeners(SavedSearch)}"
    )
