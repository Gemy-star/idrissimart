# نظام الإعلان المجاني الواحد - One Free Ad System

## التاريخ: نوفمبر 2024
## الهدف: منح كل مستخدم جديد إعلان واحد مجاني فقط

---

## 📋 نظرة عامة

تم تعديل النظام ليمنح كل مستخدم جديد **إعلان واحد مجاني فقط** بدلاً من باقة كاملة.

### القواعد الجديدة:
1. ✅ كل مستخدم جديد يحصل على **1 إعلان مجاني** عند التسجيل
2. ✅ صلاحية الإعلان المجاني: **365 يوم** (سنة كاملة)
3. ✅ بعد استخدام الإعلان المجاني، **يجب شراء باقة**
4. ✅ النظام يمنع نشر إعلانات بدون باقة نشطة

---

## 🔄 التغييرات المطبقة

### 1. تعديل UserPackage Model
**الملف:** `main/models.py`

**التغييرات:**
```python
# Before:
package = models.ForeignKey(AdPackage, on_delete=models.PROTECT)

# After:
package = models.ForeignKey(
    AdPackage,
    on_delete=models.PROTECT,
    null=True,  # ✅ يمكن أن يكون فارغاً للإعلانات المجانية
    blank=True,
    help_text=_("الباقة المرتبطة - يمكن أن تكون فارغة للإعلانات المجانية")
)
```

**تحديث __str__ method:**
```python
def __str__(self):
    package_name = self.package.name if self.package else _("إعلان مجاني")
    return f"{self.user.username} - {package_name}"
```

**تحديث save method:**
```python
def save(self, *args, **kwargs):
    if not self.pk:  # On creation
        # Only set from package if package exists
        if self.package:
            if not self.ads_remaining:
                self.ads_remaining = self.package.ad_count
            if not self.expiry_date:
                self.expiry_date = timezone.now() + timezone.timedelta(
                    days=self.package.duration_days
                )
    super().save(*args, **kwargs)
```

---

### 2. تعديل Signal للمستخدمين الجدد
**الملف:** `main/signals.py`

**Before:**
```python
@receiver(post_save, sender=User)
def assign_default_package_to_new_user(sender, instance, created, **kwargs):
    if created:
        default_package = AdPackage.objects.filter(
            is_default=True, is_active=True, price=0
        ).first()

        if default_package:
            UserPackage.objects.create(user=instance, package=default_package)
```

**After:**
```python
@receiver(post_save, sender=User)
def assign_default_package_to_new_user(sender, instance, created, **kwargs):
    """
    منح كل مستخدم جديد إعلان واحد مجاني
    Give each new user one free ad - they must buy a package after using it
    """
    if created:
        try:
            from datetime import timedelta

            UserPackage.objects.create(
                user=instance,
                package=None,  # ✅ No associated package - this is a free gift
                ads_remaining=1,  # ✅ Only 1 free ad
                expiry_date=timezone.now() + timedelta(days=365),  # ✅ Valid for 1 year
            )

            Notification.objects.create(
                user=instance,
                title=_("مرحباً بك في إدريسي مارت!"),
                message=_("تم منحك إعلان واحد مجاني! بعد استخدامه، يمكنك شراء باقة لنشر المزيد من الإعلانات."),
                notification_type=Notification.NotificationType.GENERAL,
            )
        except Exception as e:
            print(f"Error assigning free ad to user {instance.username}: {e}")
```

---

### 3. تحديث رسائل الخطأ
**الملفات:** `main/classifieds_views.py` و `main/views.py`

**Before:**
```python
messages.error(
    request,
    _("لقد استنفدت رصيدك من الإعلانات أو لا تملك باقة نشطة. يرجى اختيار باقة.")
)
```

**After:**
```python
messages.error(
    request,
    _("لقد استنفدت إعلانك المجاني! يرجى شراء باقة للاستمرار في نشر الإعلانات.")
)
```

---

### 4. Migration File
**الملف:** `main/migrations/0008_make_package_nullable_for_free_ads.py`

**الأمر المستخدم:**
```bash
python manage.py makemigrations main --name make_package_nullable_for_free_ads
```

**التغيير:**
- Alter field `package` on `userpackage` → `null=True, blank=True`

---

## 🔍 كيف يعمل النظام؟

### عند تسجيل مستخدم جديد:

```
1. User creates account
   ↓
2. post_save signal triggered
   ↓
3. UserPackage created:
   - package = None (no associated package)
   - ads_remaining = 1
   - expiry_date = now + 365 days
   ↓
4. Welcome notification sent:
   "تم منحك إعلان واحد مجاني! بعد استخدامه، يمكنك شراء باقة لنشر المزيد من الإعلانات."
```

---

### عند محاولة نشر إعلان:

```
1. User clicks "نشر إعلان"
   ↓
2. ClassifiedAdCreateView.dispatch() checks:
   - has_quota = UserPackage.objects.filter(
       user=user,
       expiry_date__gte=timezone.now(),
       ads_remaining__gt=0
     ).exists()
   ↓
3a. If has_quota == True:
    → Allow ad creation
    → Decrement ads_remaining
   ↓
3b. If has_quota == False:
    → Show error: "لقد استنفدت إعلانك المجاني!"
    → Redirect to packages_list page
```

---

## 📊 Database Schema

### UserPackage Table:
```sql
CREATE TABLE user_packages (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    package_id INTEGER NULL,  -- ✅ NOW NULLABLE
    payment_id INTEGER NULL,
    purchase_date DATETIME NOT NULL,
    expiry_date DATETIME NOT NULL,
    ads_remaining INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (package_id) REFERENCES ad_packages(id),  -- ✅ CAN BE NULL
    FOREIGN KEY (payment_id) REFERENCES payments(id)
);
```

---

## 📝 أمثلة على البيانات

### مستخدم جديد (1 إعلان مجاني):
```python
UserPackage(
    user=user_instance,
    package=None,  # ✅ Free ad - no package
    payment=None,
    ads_remaining=1,
    expiry_date="2025-11-21",  # 365 days from now
    purchase_date="2024-11-21"
)
```

### مستخدم اشترى باقة:
```python
UserPackage(
    user=user_instance,
    package=basic_package,  # ✅ Associated with package
    payment=payment_instance,
    ads_remaining=5,
    expiry_date="2024-12-21",  # 30 days from purchase
    purchase_date="2024-11-21"
)
```

---

## 🔄 User Journey

### رحلة المستخدم الجديد:

```
Day 1: Registration
├─ ✅ Account created
├─ ✅ 1 free ad granted (valid for 365 days)
└─ ✅ Welcome notification received

Day 2: First Ad
├─ User creates first ad
├─ ads_remaining: 1 → 0
└─ ✅ Ad published successfully

Day 3: Second Ad (No quota)
├─ User tries to create second ad
├─ System checks: ads_remaining = 0
├─ ❌ Blocked!
├─ Error: "لقد استنفدت إعلانك المجاني!"
└─ → Redirected to packages page

Day 3: Purchase Package
├─ User buys "Basic Package" (5 ads)
├─ ✅ New UserPackage created
└─ ads_remaining: 5

Day 4: Post More Ads
├─ User creates ad #2
├─ ads_remaining: 5 → 4
└─ ✅ Success
```

---

## 🧪 Testing Checklist

### Manual Testing:
- [ ] Create new user account
- [ ] Verify UserPackage created with:
  - package = None
  - ads_remaining = 1
  - expiry_date = now + 365 days
- [ ] Check welcome notification received
- [ ] Create first ad successfully
- [ ] Verify ads_remaining decreased to 0
- [ ] Try to create second ad
- [ ] Verify error message shown
- [ ] Verify redirect to packages page
- [ ] Purchase a package
- [ ] Verify new UserPackage created
- [ ] Create ad with purchased package
- [ ] Verify ads_remaining decreased

### Database Testing:
```sql
-- Check free ad for new user
SELECT * FROM user_packages WHERE package_id IS NULL;

-- Check all user packages
SELECT
    u.username,
    up.ads_remaining,
    up.expiry_date,
    CASE
        WHEN up.package_id IS NULL THEN 'Free Ad'
        ELSE ap.name
    END as package_name
FROM user_packages up
JOIN users u ON up.user_id = u.id
LEFT JOIN ad_packages ap ON up.package_id = ap.id
ORDER BY up.purchase_date DESC;
```

---

## ⚠️ Important Notes

### للمطورين:
1. **package field is now nullable** - تأكد من التعامل مع None
2. **Free ads have no associated package** - تحقق من `if package:` قبل الوصول
3. **Signal creates UserPackage without package** - لا حاجة لباقة افتراضية
4. **Error messages updated** - استخدم الرسائل الجديدة

### للمديرين:
1. **لا حاجة لباقة افتراضية** - يمكن حذف is_default packages
2. **كل مستخدم جديد = 1 إعلان** - لا استثناءات
3. **Expiry = 365 days** - صلاحية سنة كاملة
4. **No automatic renewal** - المستخدم يجب أن يشتري باقة

---

## 🚀 Deployment Steps

### Before Migration:
```bash
# 1. Backup database
python manage.py dumpdata main.UserPackage > userpackages_backup.json

# 2. Check existing free packages
python manage.py shell
>>> from main.models import AdPackage, UserPackage
>>> AdPackage.objects.filter(is_default=True, price=0).count()
```

### Run Migration:
```bash
# 1. Make migrations
python manage.py makemigrations main

# 2. Check SQL
python manage.py sqlmigrate main 0008

# 3. Run migration
python manage.py migrate main

# 4. Verify
python manage.py shell
>>> from main.models import UserPackage
>>> UserPackage._meta.get_field('package').null
True  # ✅ Should be True
```

### After Migration:
```bash
# Test new user registration
python manage.py shell
>>> from main.models import User, UserPackage
>>> user = User.objects.create_user('testuser', 'test@example.com', 'password123')
>>> UserPackage.objects.filter(user=user).first()
<UserPackage: testuser - إعلان مجاني>  # ✅ Success
```

---

## 📈 Expected Impact

### User Behavior:
- ✅ Lower barrier to entry (1 free ad)
- ✅ Encourages package purchase after testing
- ✅ Clearer monetization path

### Business Metrics:
- 📊 Track free ad usage rate
- 📊 Track conversion rate (free → paid)
- 📊 Track average time to first package purchase

### Database:
- 📊 Monitor UserPackage records with package=NULL
- 📊 Track expiry dates
- 📊 Monitor ads_remaining = 0 records

---

## 🔧 Troubleshooting

### Issue: "package cannot be NULL" error
**Solution:** Run migration 0008_make_package_nullable_for_free_ads

### Issue: New users not getting free ad
**Solution:** Check signal in signals.py is registered

### Issue: Old users have default packages
**Solution:** This is expected - only new users get 1 free ad

### Issue: Error message in English
**Solution:** Check LANGUAGE_CODE in settings and translation files

---

## 📚 Related Files

- `main/models.py` - UserPackage model
- `main/signals.py` - assign_default_package_to_new_user signal
- `main/classifieds_views.py` - ClassifiedAdCreateView
- `main/views.py` - enhanced_ad_create_view
- `main/migrations/0008_make_package_nullable_for_free_ads.py` - Migration file

---

## ✅ Summary

**Previous System:**
- New users get default package with multiple ads
- Required is_default=True packages in database

**New System:**
- New users get exactly 1 free ad
- No package associated (package=None)
- Valid for 365 days
- Must buy package after using free ad

**Benefits:**
- ✅ Simpler implementation
- ✅ No dependency on default packages
- ✅ Clearer user expectations
- ✅ Better monetization strategy
- ✅ Encourages package purchases

---

تم تنفيذ النظام بنجاح! 🎉
