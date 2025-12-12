"""
Test script for blocked words validation
"""

from main.blocked_words import is_username_allowed, contains_blocked_word

# Test cases for username validation
test_usernames = [
    # Should be blocked - Admin variations
    ("admin", False),
    ("Admin123", False),
    ("ادمن", False),
    ("أدمن_user", False),
    ("user_admin", False),
    ("adm1n", False),

    # Should be blocked - Site name
    ("idrissimart", False),
    ("إدريسي_مارت", False),
    ("ادريسيمارت", False),
    ("idrissi", False),

    # Should be blocked - Offensive words
    ("user_sex_123", False),
    ("porn_user", False),
    ("سكس_user", False),

    # Should be allowed - Normal usernames
    ("ahmed_mohamed", True),
    ("user123", True),
    ("محمد_احمد", True),
    ("engineer_ali", True),
    ("company_tech", True),
]

print("=" * 60)
print("Testing Username Validation")
print("=" * 60)

for username, should_allow in test_usernames:
    is_allowed, message = is_username_allowed(username)
    status = "✓ PASS" if (is_allowed == should_allow) else "✗ FAIL"

    print(f"\n{status} | Username: {username}")
    print(f"   Expected: {'Allowed' if should_allow else 'Blocked'}")
    print(f"   Result: {'Allowed' if is_allowed else 'Blocked'}")
    if not is_allowed:
        print(f"   Reason: {message}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
