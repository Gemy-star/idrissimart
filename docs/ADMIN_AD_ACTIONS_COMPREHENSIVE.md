# دليل إجراءات الإعلانات في داش بورد الأدمن
## Admin Ad Actions Guide

تم إنشاء هذا الدليل في: 2026-01-09

---

## 📋 نظرة عامة - الإجراءات الموجودة

### ✅ الإجراءات المُنفذة حالياً:

#### 1. **الموافقة والرفض**
- ✅ `approve_ad_view` - الموافقة على الإعلان (حالة ACTIVE)
- ✅ `reject_ad_view` - رفض الإعلان (حالة REJECTED) مع السبب
- ✅ `ad_quick_review_ajax` - مراجعة سريعة عبر AJAX
- ✅ `bulk_approve_ads` - موافقة جماعية
- ✅ `AdminChangeAdStatusView` - تغيير الحالة (approve/reject)

**الحالات:** PENDING → ACTIVE أو REJECTED

#### 2. **التعليق والتفعيل**
- ✅ `admin_suspend_ad` - تعليق الإعلان (حالة suspended)
- ✅ `admin_activate_ad` - تفعيل إعلان معلق

**الحالات:** ACTIVE ↔ SUSPENDED

#### 3. **الإخفاء والإظهار**
- ✅ `ToggleAdHideView` - إخفاء/إظهار الإعلان (is_hidden)
- يخفي الإعلان من القوائم العامة
- الإعلان يظل موجوداً لكن مخفي

#### 4. **الحذف**
- ✅ `AdminAdDeleteView` - حذف الإعلان (soft delete)
- ✅ `DeleteAdView` - حذف الإعلان مع إشعار
- ✅ `bulk_delete_ads` - حذف جماعي

#### 5. **الميزات الإضافية**
- ✅ `admin_toggle_featured` - تبديل حالة المميز (is_highlighted)
- ✅ `admin_toggle_urgent` - تبديل حالة العاجل (is_urgent)
- ✅ `admin_toggle_pinned` - تبديل حالة المثبت (is_pinned)
- ✅ `AdminToggleAdFeatureView` - تبديل الميزات عبر AJAX

#### 6. **السلة**
- ✅ `EnableAdCartView` - تفعيل السلة للإعلان (cart_enabled_by_admin)
- ✅ `admin_ad_toggle_cart` - تبديل حالة السلة

#### 7. **التمديد**
- ✅ `admin_extend_ad` - تمديد تاريخ انتهاء الإعلان
- يضيف عدد أيام محدد (افتراضي: 30 يوم)

#### 8. **تغيير القسم**
- ✅ `admin_change_ad_category` - تغيير قسم/فئة الإعلان
- ✅ `admin_ad_change_category` - نسخة أخرى من views.py

#### 9. **التعديل**
- ✅ `AdminAdUpdateView` - تعديل بيانات الإعلان (form-based)
- تعديل الحقول الأساسية فقط

#### 10. **الإجراءات الجماعية**
- ✅ `admin_bulk_actions` - إجراءات متعددة:
  - approve: موافقة جماعية
  - reject: رفض جماعي
  - suspend: تعليق جماعي
  - activate: تفعيل جماعي
  - delete: حذف جماعي
  - featured_on/off: تمييز جماعي
  - urgent_on/off: عاجل جماعي
  - pin/unpin: تثبيت جماعي

---

## ⚠️ الإجراءات الناقصة

### 1. ❌ **تعديل كامل المحتوى** (شامل)
**المطلوب:**
- تعديل جميع الحقول (العنوان، الوصف، السعر، الخ)
- تعديل/حذف/إضافة الصور
- تعديل القيم المخصصة (custom fields)
- تعديل موقع الإعلان
- تعديل معلومات الاتصال

**الحل:** إنشاء `AdminAdFullEditView`

### 2. ❌ **نسخ/تكرار الإعلان**
**المطلوب:**
- عمل نسخة كاملة من الإعلان
- نسخ الصور والحقول المخصصة

**الحل:** إنشاء `admin_duplicate_ad`

### 3. ❌ **الحظر (Ban)**
**المطلوب:**
- حظر نهائي للإعلان (حالة BANNED)
- منع إعادة نشره

**الحل:** إنشاء `admin_ban_ad` مع حالة جديدة

### 4. ❌ **إلغاء الحظر (Unban)**
**المطلوب:**
- إلغاء الحظر وإعادة الإعلان لحالة سابقة

**الحل:** إنشاء `admin_unban_ad`

### 5. ❌ **المسح النهائي (Hard Delete)**
**المطلوب:**
- حذف نهائي من قاعدة البيانات
- حذف كل البيانات المرتبطة (صور، تقييمات، الخ)

**الحل:** إنشاء `admin_permanent_delete_ad`

### 6. ❌ **نقل ملكية الإعلان**
**المطلوب:**
- نقل الإعلان إلى مستخدم آخر

**الحل:** إنشاء `admin_transfer_ad_ownership`

### 7. ❌ **إعادة نشر الإعلان**
**المطلوب:**
- إعادة نشر إعلان منتهي

**الحل:** إنشاء `admin_republish_ad`

### 8. ❌ **إحصائيات الإعلان**
**المطلوب:**
- عرض إحصائيات تفصيلية (مشاهدات، نقرات، رسائل)

**الحل:** إنشاء `admin_ad_statistics`

---

## 🔧 الإجراءات التي سأضيفها الآن

### 1. تعديل كامل المحتوى (Full Edit)
### 2. نسخ الإعلان (Duplicate)
### 3. حظر/إلغاء الحظر (Ban/Unban)
### 4. مسح نهائي (Hard Delete)
### 5. نقل الملكية (Transfer Ownership)

---

## 📍 مواقع الـ URLs

### الموجودة:
```python
# main/urls.py
path("admin/ads/<int:ad_id>/approve/", approve_ad_view)
path("admin/ads/<int:ad_id>/reject/", reject_ad_view)
path("admin/ads/<int:ad_id>/suspend/", admin_suspend_ad)
path("admin/ads/<int:ad_id>/activate/", admin_activate_ad)
path("admin/ads/<int:ad_id>/extend/", admin_extend_ad)
path("admin/ads/<int:ad_id>/toggle-featured/", admin_toggle_featured)
path("admin/ads/<int:ad_id>/toggle-urgent/", admin_toggle_urgent)
path("admin/ads/<int:ad_id>/toggle-pinned/", admin_toggle_pinned)
path("admin/ads/<int:ad_id>/change-category/", admin_change_ad_category)
path("admin/ads/bulk-actions/", admin_bulk_actions)
path("admin/ads/<int:ad_id>/toggle-hide/", ToggleAdHideView)
path("admin/ads/<int:ad_id>/enable-cart/", EnableAdCartView)
path("admin/ads/<int:ad_id>/delete/", AdminAdDeleteView)
```

### سأضيفها:
```python
path("admin/ads/<int:ad_id>/full-edit/", admin_ad_full_edit)
path("admin/ads/<int:ad_id>/duplicate/", admin_duplicate_ad)
path("admin/ads/<int:ad_id>/ban/", admin_ban_ad)
path("admin/ads/<int:ad_id>/unban/", admin_unban_ad)
path("admin/ads/<int:ad_id>/permanent-delete/", admin_permanent_delete_ad)
path("admin/ads/<int:ad_id>/transfer-ownership/", admin_transfer_ownership)
```

---

## 📊 جدول مقارنة الحالات

| الإجراء | الحالة النهائية | القابلية للعكس | الإشعار |
|---------|----------------|----------------|---------|
| **approve** | ACTIVE | نعم (reject) | ✅ |
| **reject** | REJECTED | نعم (approve) | ✅ |
| **suspend** | SUSPENDED | نعم (activate) | ✅ |
| **activate** | ACTIVE | نعم (suspend) | ✅ |
| **ban** | BANNED | نعم (unban) | ✅ |
| **hide** | is_hidden=True | نعم (unhide) | ✅ |
| **delete** | محذوف | لا (نهائي) | ✅ |
| **extend** | expires_at += days | لا | ✅ |
| **featured** | is_highlighted | نعم (toggle) | ❌ |
| **urgent** | is_urgent | نعم (toggle) | ❌ |
| **pinned** | is_pinned | نعم (toggle) | ❌ |

---

## 🎯 سأبدأ الآن بإضافة الإجراءات الناقصة...
