#!/bin/bash

# ===========================
# Translation Setup Script
# ===========================

echo "🌍 إعداد نظام الترجمة..."

# ألوان للمخرجات
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ===========================
# 1. إنشاء مجلد locale
# ===========================
echo -e "\n${YELLOW}1. إنشاء مجلد locale...${NC}"
if [ ! -d "locale" ]; then
    mkdir -p locale
    echo -e "${GREEN}✓ تم إنشاء مجلد locale${NC}"
else
    echo -e "${GREEN}✓ مجلد locale موجود بالفعل${NC}"
fi

# ===========================
# 2. التحقق من إعدادات Django
# ===========================
echo -e "\n${YELLOW}2. التحقق من إعدادات Django...${NC}"

# التحقق من وجود USE_I18N في settings
if grep -q "USE_I18N = True" */settings*.py 2>/dev/null; then
    echo -e "${GREEN}✓ USE_I18N مفعل${NC}"
else
    echo -e "${RED}✗ تحذير: USE_I18N غير موجود أو غير مفعل${NC}"
    echo -e "${YELLOW}أضف إلى settings.py:${NC}"
    echo "USE_I18N = True"
    echo "LANGUAGE_CODE = 'ar'"
fi

# ===========================
# 3. إنشاء ملفات الرسائل
# ===========================
echo -e "\n${YELLOW}3. إنشاء ملفات الترجمة...${NC}"

# العربية
echo -e "${YELLOW}   → إنشاء ملف الترجمة العربية...${NC}"
python manage.py makemessages -l ar --no-obsolete
if [ $? -eq 0 ]; then
    echo -e "${GREEN}   ✓ تم إنشاء locale/ar/LC_MESSAGES/django.po${NC}"
else
    echo -e "${RED}   ✗ فشل إنشاء الملف العربي${NC}"
fi

# الإنجليزية
echo -e "${YELLOW}   → إنشاء ملف الترجمة الإنجليزية...${NC}"
python manage.py makemessages -l en --no-obsolete
if [ $? -eq 0 ]; then
    echo -e "${GREEN}   ✓ تم إنشاء locale/en/LC_MESSAGES/django.po${NC}"
else
    echo -e "${RED}   ✗ فشل إنشاء الملف الإنجليزي${NC}"
fi

# ===========================
# 4. التحقق من الملفات
# ===========================
echo -e "\n${YELLOW}4. التحقق من الملفات المُنشأة...${NC}"

if [ -f "locale/ar/LC_MESSAGES/django.po" ]; then
    lines=$(wc -l < "locale/ar/LC_MESSAGES/django.po")
    echo -e "${GREEN}✓ ملف العربية موجود (${lines} سطر)${NC}"
else
    echo -e "${RED}✗ ملف العربية غير موجود${NC}"
fi

if [ -f "locale/en/LC_MESSAGES/django.po" ]; then
    lines=$(wc -l < "locale/en/LC_MESSAGES/django.po")
    echo -e "${GREEN}✓ ملف الإنجليزية موجود (${lines} سطر)${NC}"
else
    echo -e "${RED}✗ ملف الإنجليزية غير موجود${NC}"
fi

# ===========================
# 5. إضافة الترجمات الأساسية
# ===========================
echo -e "\n${YELLOW}5. إضافة ترجمات أساسية...${NC}"

# إنشاء ملف مساعد بالترجمات
cat > locale/translations_helper.txt << 'EOF'
# ===========================
# الترجمات الأساسية المطلوبة
# انسخ هذه إلى locale/ar/LC_MESSAGES/django.po
# ===========================

msgid "Item added to cart"
msgstr "تمت إضافة المنتج إلى السلة"

msgid "Item removed from cart"
msgstr "تمت إزالة المنتج من السلة"

msgid "Item already in cart"
msgstr "المنتج موجود بالفعل في السلة"

msgid "Item not in cart"
msgstr "المنتج غير موجود في السلة"

msgid "Item added to wishlist"
msgstr "تمت إضافة المنتج إلى المفضلة"

msgid "Item removed from wishlist"
msgstr "تمت إزالة المنتج من المفضلة"

msgid "Item already in wishlist"
msgstr "المنتج موجود بالفعل في المفضلة"

msgid "Item not in wishlist"
msgstr "المنتج غير موجود في المفضلة"

msgid "Country updated successfully"
msgstr "تم تحديث الدولة بنجاح"

msgid "Invalid country code"
msgstr "كود الدولة غير صالح"

msgid "Item ID required"
msgstr "معرف المنتج مطلوب"
EOF

echo -e "${GREEN}✓ تم إنشاء ملف مساعد: locale/translations_helper.txt${NC}"
echo -e "${YELLOW}   → انسخ المحتوى إلى ملفات .po الخاصة بك${NC}"

# ===========================
# 6. تجميع الترجمات
# ===========================
echo -e "\n${YELLOW}6. تجميع الترجمات...${NC}"
echo -e "${YELLOW}   ملاحظة: قد تحتاج إلى تحرير الملفات أولاً${NC}"
read -p "هل تريد تجميع الترجمات الآن؟ (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py compilemessages
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ تم تجميع الترجمات بنجاح${NC}"
    else
        echo -e "${RED}✗ فشل تجميع الترجمات${NC}"
    fi
else
    echo -e "${YELLOW}⊘ تم تخطي التجميع${NC}"
fi

# ===========================
# 7. اختبار الترجمات
# ===========================
echo -e "\n${YELLOW}7. اختبار الترجمات...${NC}"

cat > test_translations.py << 'EOF'
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils.translation import activate, gettext as _

print("\n=== اختبار الترجمات ===\n")

# اختبار العربية
activate('ar')
print(f"العربية (ar):")
print(f"  - {_('Item added to cart')}")
print(f"  - {_('Item removed from cart')}")
print(f"  - {_('Country updated successfully')}")

# اختبار الإنجليزية
activate('en')
print(f"\nEnglish (en):")
print(f"  - {_('Item added to cart')}")
print(f"  - {_('Item removed from cart')}")
print(f"  - {_('Country updated successfully')}")
EOF

echo -e "${GREEN}✓ تم إنشاء سكريبت اختبار: test_translations.py${NC}"
echo -e "${YELLOW}   → نفذ: python test_translations.py${NC}"

# ===========================
# 8. ملخص
# ===========================
echo -e "\n${GREEN}=========================${NC}"
echo -e "${GREEN}🎉 اكتمل الإعداد!${NC}"
echo -e "${GREEN}=========================${NC}"

echo -e "\n${YELLOW}الخطوات التالية:${NC}"
echo "1. حرر الملفات:"
echo "   - locale/ar/LC_MESSAGES/django.po"
echo "   - locale/en/LC_MESSAGES/django.po"
echo ""
echo "2. أضف الترجمات من: locale/translations_helper.txt"
echo ""
echo "3. جمّع الترجمات:"
echo "   python manage.py compilemessages"
echo ""
echo "4. اختبر الترجمات:"
echo "   python test_translations.py"
echo ""
echo "5. أعد تشغيل Django server"
echo ""

echo -e "${GREEN}✨ استمتع بالترجمات! ✨${NC}"
