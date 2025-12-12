"""
Blocked/Banned words for usernames and content
"""

# Reserved system words (Arabic and English)
RESERVED_WORDS = [
    # Admin related
    "admin",
    "ادمن",
    "أدمن",
    "مدير",
    "مشرف",
    "administrator",
    "moderator",
    # Site name variations
    "idrissimart",
    "إدريسي مارت",
    "ادريسي مارت",
    "إدريسيمارت",
    "ادريسيمارت",
    "idrissi",
    "إدريسي",
    "ادريسي",
    "idrisi",
    "edrissi",
    "edrisi",
    # System roles
    "root",
    "superuser",
    "system",
    "staff",
    "support",
    "دعم",
    "مساعد",
    "webmaster",
    "sysadmin",
    "owner",
    "مالك",
    # Variations with numbers/special chars
    "adm1n",
    "adm!n",
    "@dmin",
    "4dmin",
    "admln",
]

# Offensive/Inappropriate words (Arabic and English)
OFFENSIVE_WORDS = [
    # Common offensive terms in Arabic
    "زانى",
    "زانية",
    "عاهر",
    "عاهرة",
    "شرموط",
    "شرموطة",
    "قحبة",
    "قحبه",
    "كلب",
    "حيوان",
    "خنزير",
    "حمار",
    "غبي",
    "احمق",
    # English offensive terms
    "sex",
    "porn",
    "xxx",
    "adult",
    "fuck",
    "shit",
    "damn",
    "bitch",
    "prostitute",
    "whore",
    "slut",
    "bastard",
    "asshole",
    "dick",
    # Sexual/adult content
    "جنس",
    "سكس",
    "نيك",
    "جماع",
    "دعارة",
    "اباحي",
    "اباحية",
    "nude",
    "naked",
    "escort",
    "hookup",
    # Hate speech
    "كافر",
    "ملحد",
    "يهودي",
    "نصراني",
    "مجوسي",
    "racist",
    "nazi",
    "terrorist",
    "terrorism",
    # Spam/scam related
    "casino",
    "viagra",
    "cialis",
    "lottery",
    "winner",
    "كازينو",
    "قمار",
    # Variations with numbers/special chars
    "s3x",
    "p0rn",
    "fvck",
    "sh!t",
    "b!tch",
]

# Common suspicious patterns
SUSPICIOUS_PATTERNS = [
    "admin",
    "mod",
    "root",
    "sys",
    "test",
    "demo",
    "null",
    "undefined",
    "official",
    "verified",
    "vip",
    "premium",
    "staff",
    "رسمي",
    "موثق",
    "مميز",
    "خاص",
]


def contains_blocked_word(text, check_offensive=True, check_reserved=True):
    """
    Check if text contains any blocked words

    Args:
        text: The text to check (username, etc.)
        check_offensive: Whether to check offensive words
        check_reserved: Whether to check reserved words

    Returns:
        tuple: (is_blocked, reason) where reason explains why it's blocked
    """
    if not text:
        return False, ""

    # Normalize text for checking
    text_lower = text.lower().strip()
    text_normalized = (
        text_lower.replace(" ", "").replace("_", "").replace("-", "").replace(".", "")
    )

    # Check reserved words
    if check_reserved:
        for word in RESERVED_WORDS:
            word_normalized = word.lower().replace(" ", "")
            if word_normalized in text_normalized:
                return True, f"الاسم يحتوي على كلمة محجوزة: {word}"

    # Check offensive words
    if check_offensive:
        for word in OFFENSIVE_WORDS:
            word_normalized = word.lower().replace(" ", "")
            if word_normalized in text_normalized:
                return True, "الاسم يحتوي على كلمة غير لائقة"

    return False, ""


def is_username_allowed(username):
    """
    Check if username is allowed

    Args:
        username: The username to validate

    Returns:
        tuple: (is_allowed, error_message)
    """
    is_blocked, reason = contains_blocked_word(
        username, check_offensive=True, check_reserved=True
    )

    if is_blocked:
        return False, reason

    return True, ""


def clean_text_content(text):
    """
    Check if text content contains offensive words
    Used for ads, comments, messages, etc.

    Args:
        text: The text content to check

    Returns:
        tuple: (is_clean, list_of_issues)
    """
    issues = []

    # Check for offensive words
    is_blocked, reason = contains_blocked_word(
        text,
        check_offensive=True,
        check_reserved=False,  # Don't check reserved words in content
    )

    if is_blocked:
        issues.append(reason)

    return len(issues) == 0, issues
