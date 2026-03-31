# -*- coding: utf-8 -*-
"""
Management command to seed EmailTemplate with realistic bilingual (AR/EN) content.

Usage:
    python manage.py seed_email_templates               # insert new, skip existing
    python manage.py seed_email_templates --overwrite   # replace all existing
    python manage.py seed_email_templates --key welcome # seed only one key
"""

from django.core.management.base import BaseCommand

# ---------------------------------------------------------------------------
# Shared inline CSS block (reused in every template body)
# ---------------------------------------------------------------------------
BASE_CSS = """
<style>
  body{margin:0;padding:0;background:#f5f7fa;font-family:'Segoe UI',Tahoma,Arial,sans-serif;direction:rtl;text-align:right;color:#333;}
  .wrap{background:#f5f7fa;padding:30px 15px;}
  .box{max-width:600px;margin:0 auto;background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 6px 20px rgba(0,0,0,.08);}
  .hdr{background:linear-gradient(135deg,#4b315e 0%,#6b4c7a 50%,#ff8534 100%);color:#fff;padding:40px 30px;text-align:center;}
  .hdr h1{margin:0 0 8px;font-size:24px;}
  .hdr p{margin:0;font-size:15px;opacity:.9;}
  .logo{font-size:32px;font-weight:700;margin-bottom:6px;display:block;}
  .body{padding:36px 30px;line-height:1.8;}
  .body p{margin:0 0 14px;font-size:15px;color:#444;}
  .btn-wrap{text-align:center;margin:28px 0;}
  .btn{display:inline-block;background:linear-gradient(135deg,#6b4c7a,#ff8534);color:#fff!important;padding:14px 40px;border-radius:8px;text-decoration:none;font-weight:700;font-size:15px;}
  .info-box{background:#fdf6ff;border-right:4px solid #6b4c7a;border-radius:6px;padding:16px 18px;margin:18px 0;font-size:14px;color:#555;}
  .warn-box{background:#fff8ec;border-right:4px solid #ff8534;border-radius:6px;padding:16px 18px;margin:18px 0;font-size:14px;color:#7a5c00;}
  .success-box{background:#ecfdf5;border-right:4px solid #059669;border-radius:6px;padding:16px 18px;margin:18px 0;font-size:14px;color:#065f46;}
  .otp-box{background:#f3e8ff;border:2px dashed #6b4c7a;border-radius:10px;padding:20px;text-align:center;margin:24px 0;}
  .otp-code{font-size:40px;font-weight:700;letter-spacing:10px;color:#4b315e;font-family:monospace;}
  .divider{border:0;border-top:1px solid #eee;margin:22px 0;}
  .ftr{background:#f8f8f8;border-top:1px solid #eee;padding:20px 30px;text-align:center;font-size:12px;color:#999;}
  .ftr a{color:#6b4c7a;text-decoration:none;}
  table{width:100%;border-collapse:collapse;}
  td{padding:10px;border-bottom:1px solid #eee;font-size:14px;}
  td.lbl{font-weight:600;color:#666;width:40%;}
</style>
"""


def _html(header_title_ar, header_subtitle_ar, header_title_en, header_subtitle_en, body_ar, body_en):
    """Build self-contained bilingual HTML template."""
    footer_ar = (
        "<p>هذه رسالة تلقائية، يرجى عدم الرد عليها.</p>"
        "<p>© {{site_name}} — جميع الحقوق محفوظة.</p>"
    )
    footer_en = (
        "<p>This is an automated message, please do not reply.</p>"
        "<p>© {{site_name}} — All rights reserved.</p>"
    )
    ar_html = (
        f"<!DOCTYPE html><html lang='ar' dir='rtl'><head><meta charset='UTF-8'>"
        f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"{BASE_CSS}</head><body><div class='wrap'><div class='box'>"
        f"<div class='hdr'><span class='logo'>{{{{site_name}}}}</span>"
        f"<h1>{header_title_ar}</h1><p>{header_subtitle_ar}</p></div>"
        f"<div class='body'>{body_ar}</div>"
        f"<div class='ftr'>{footer_ar}</div>"
        f"</div></div></body></html>"
    )
    en_html = (
        f"<!DOCTYPE html><html lang='en' dir='ltr'><head><meta charset='UTF-8'>"
        f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"{BASE_CSS}</head><body style='direction:ltr;text-align:left;'>"
        f"<div class='wrap'><div class='box'>"
        f"<div class='hdr'><span class='logo'>{{{{site_name}}}}</span>"
        f"<h1>{header_title_en}</h1><p>{header_subtitle_en}</p></div>"
        f"<div class='body' style='text-align:left;'>{body_en}</div>"
        f"<div class='ftr'>{footer_en}</div>"
        f"</div></div></body></html>"
    )
    return ar_html, en_html


# ---------------------------------------------------------------------------
# Template definitions  — key: (name, name_ar, subject_ar, subject_en, variables, ar_body, en_body)
# ---------------------------------------------------------------------------

def _welcome():
    ar_body = """
<p>مرحباً <strong>{{user_name}}</strong>،</p>
<p>يسعدنا انضمامك إلى <strong>{{site_name}}</strong> — المنصة المتكاملة للإعلانات المبوبة.</p>
<div class='success-box'>
  <strong>حسابك جاهز!</strong> يمكنك الآن نشر إعلاناتك، التسوق، والاستفادة من جميع خدمات المنصة.
</div>
<div class='btn-wrap'><a href='{{site_url}}' class='btn'>ابدأ الاستكشاف</a></div>
<hr class='divider'>
<p>إذا واجهتك أي مشكلة، فريق الدعم دائماً في خدمتك.</p>
"""
    en_body = """
<p>Hello <strong>{{user_name}}</strong>,</p>
<p>Welcome to <strong>{{site_name}}</strong> — your all-in-one classified ads platform!</p>
<div class='success-box' style='border-left:4px solid #059669;border-right:none;'>
  <strong>Your account is ready!</strong> You can now post ads, shop, and enjoy all platform features.
</div>
<div class='btn-wrap'><a href='{{site_url}}' class='btn'>Start Exploring</a></div>
<hr class='divider'>
<p>If you ever need help, our support team is always here for you.</p>
"""
    ar, en = _html("مرحباً بك!", "نحن سعداء بانضمامك", "Welcome!", "We're glad to have you", ar_body, en_body)
    return dict(
        key="welcome", name="Welcome Email", name_ar="بريد الترحيب",
        subject="مرحباً بك في {{site_name}}", subject_ar="مرحباً بك في {{site_name}}",
        body=en, body_ar=ar,
        available_variables="{{user_name}}\n{{site_name}}\n{{site_url}}",
    )


def _password_reset():
    ar_body = """
<p>مرحباً <strong>{{user_name}}</strong>،</p>
<p>تلقينا طلباً لإعادة تعيين كلمة المرور الخاصة بحسابك.</p>
<div class='btn-wrap'><a href='{{reset_link}}' class='btn'>إعادة تعيين كلمة المرور</a></div>
<div class='warn-box'>
  هذا الرابط صالح لمدة <strong>24 ساعة</strong> فقط. إذا لم تطلب ذلك، يمكنك تجاهل هذه الرسالة بأمان.
</div>
<hr class='divider'>
<p style='font-size:13px;color:#888;'>إذا لم يعمل الزر، انسخ الرابط التالي في متصفحك:<br><a href='{{reset_link}}' style='color:#6b4c7a;'>{{reset_link}}</a></p>
"""
    en_body = """
<p>Hello <strong>{{user_name}}</strong>,</p>
<p>We received a request to reset the password for your account.</p>
<div class='btn-wrap'><a href='{{reset_link}}' class='btn'>Reset My Password</a></div>
<div class='warn-box' style='border-left:4px solid #ff8534;border-right:none;'>
  This link is valid for <strong>24 hours</strong> only. If you didn't request this, you can safely ignore this email.
</div>
<hr class='divider'>
<p style='font-size:13px;color:#888;'>If the button doesn't work, copy this link into your browser:<br><a href='{{reset_link}}' style='color:#6b4c7a;'>{{reset_link}}</a></p>
"""
    ar, en = _html("إعادة تعيين كلمة المرور", "اتبع التعليمات أدناه", "Password Reset", "Follow the instructions below", ar_body, en_body)
    return dict(
        key="password_reset", name="Password Reset Email", name_ar="إعادة تعيين كلمة المرور",
        subject="{{site_name}} - إعادة تعيين كلمة المرور", subject_ar="{{site_name}} - إعادة تعيين كلمة المرور",
        body=en, body_ar=ar,
        available_variables="{{user_name}}\n{{site_name}}\n{{reset_link}}",
    )


def _email_verification():
    ar_body = """
<p>مرحباً <strong>{{user_name}}</strong>،</p>
<p>شكراً لتسجيلك في <strong>{{site_name}}</strong>! خطوة واحدة تفصلك عن الانضمام الكامل.</p>
<div class='btn-wrap'><a href='{{verification_link}}' class='btn'>تأكيد البريد الإلكتروني</a></div>
<div class='info-box'>
  هذا الرابط صالح لمدة <strong>24 ساعة</strong>. إذا لم تقم بإنشاء حساب، يمكنك تجاهل هذه الرسالة.
</div>
<hr class='divider'>
<p style='font-size:13px;color:#888;'>إذا لم يعمل الزر:<br><a href='{{verification_link}}' style='color:#6b4c7a;'>{{verification_link}}</a></p>
"""
    en_body = """
<p>Hello <strong>{{user_name}}</strong>,</p>
<p>Thank you for signing up at <strong>{{site_name}}</strong>! One step left to activate your account.</p>
<div class='btn-wrap'><a href='{{verification_link}}' class='btn'>Verify My Email</a></div>
<div class='info-box' style='border-left:4px solid #6b4c7a;border-right:none;'>
  This link is valid for <strong>24 hours</strong>. If you didn't create an account, you can safely ignore this email.
</div>
<hr class='divider'>
<p style='font-size:13px;color:#888;'>If the button doesn't work:<br><a href='{{verification_link}}' style='color:#6b4c7a;'>{{verification_link}}</a></p>
"""
    ar, en = _html("تأكيد البريد الإلكتروني", "خطوة واحدة للانضمام", "Email Verification", "One step to join", ar_body, en_body)
    return dict(
        key="email_verification", name="Email Verification", name_ar="تأكيد البريد الإلكتروني",
        subject="{{site_name}} - تأكيد البريد الإلكتروني", subject_ar="{{site_name}} - تأكيد البريد الإلكتروني",
        body=en, body_ar=ar,
        available_variables="{{user_name}}\n{{site_name}}\n{{verification_link}}",
    )


def _otp_verification():
    ar_body = """
<p>مرحباً <strong>{{user_name}}</strong>،</p>
<p>رمز التحقق الخاص بحسابك في <strong>{{site_name}}</strong>:</p>
<div class='otp-box'>
  <div class='otp-code'>{{otp_code}}</div>
  <p style='margin:8px 0 0;font-size:13px;color:#666;'>صالح لمدة <strong>{{expiry_minutes}} دقيقة</strong></p>
</div>
<div class='warn-box'>
  لا تشارك هذا الرمز مع أي شخص. لن يطلب منك فريقنا هذا الرمز أبداً.
</div>
"""
    en_body = """
<p>Hello <strong>{{user_name}}</strong>,</p>
<p>Your verification code for <strong>{{site_name}}</strong>:</p>
<div class='otp-box'>
  <div class='otp-code'>{{otp_code}}</div>
  <p style='margin:8px 0 0;font-size:13px;color:#666;'>Valid for <strong>{{expiry_minutes}} minutes</strong></p>
</div>
<div class='warn-box' style='border-left:4px solid #ff8534;border-right:none;'>
  Never share this code with anyone. Our team will never ask for this code.
</div>
"""
    ar, en = _html("رمز التحقق", "استخدمه قبل انتهاء الصلاحية", "Verification Code", "Use it before it expires", ar_body, en_body)
    return dict(
        key="otp_verification", name="OTP Verification Email", name_ar="رمز التحقق",
        subject="{{site_name}} - رمز التحقق: {{otp_code}}", subject_ar="{{site_name}} - رمز التحقق: {{otp_code}}",
        body=en, body_ar=ar,
        available_variables="{{user_name}}\n{{site_name}}\n{{otp_code}}\n{{expiry_minutes}}",
    )


def _ad_approved():
    ar_body = """
<p>مرحباً <strong>{{user_name}}</strong>،</p>
<p>يسعدنا إعلامك بأن إعلانك <strong>«{{ad_title}}»</strong> تمت الموافقة عليه وهو الآن نشط على المنصة!</p>
<div class='success-box'>
  ✅ إعلانك مرئي للمستخدمين الآن. يمكنك تعزيزه بخيارات الإبراز لزيادة ظهوره.
</div>
<div class='btn-wrap'><a href='{{ad_url}}' class='btn'>عرض إعلانك</a></div>
<p>شكراً لثقتك في <strong>{{site_name}}</strong>.</p>
"""
    en_body = """
<p>Hello <strong>{{user_name}}</strong>,</p>
<p>Great news! Your ad <strong>"{{ad_title}}"</strong> has been approved and is now live on the platform!</p>
<div class='success-box' style='border-left:4px solid #059669;border-right:none;'>
  ✅ Your ad is now visible to users. Consider boosting it for extra visibility.
</div>
<div class='btn-wrap'><a href='{{ad_url}}' class='btn'>View Your Ad</a></div>
<p>Thank you for using <strong>{{site_name}}</strong>.</p>
"""
    ar, en = _html("تمت الموافقة على إعلانك!", "إعلانك نشط الآن", "Your Ad is Approved!", "Your ad is now live", ar_body, en_body)
    return dict(
        key="ad_approved", name="Ad Approved Email", name_ar="بريد قبول الإعلان",
        subject="{{site_name}} - تمت الموافقة على إعلانك", subject_ar="{{site_name}} - تمت الموافقة على إعلانك «{{ad_title}}»",
        body=en, body_ar=ar,
        available_variables="{{user_name}}\n{{site_name}}\n{{ad_title}}\n{{ad_url}}",
    )


def _ad_rejected():
    ar_body = """
<p>مرحباً <strong>{{user_name}}</strong>،</p>
<p>نأسف لإعلامك بأن إعلانك <strong>«{{ad_title}}»</strong> لم يتم قبوله في الوقت الحالي.</p>
<div class='warn-box'>
  <strong>السبب:</strong> {{reject_reason}}
</div>
<p>يمكنك تعديل الإعلان وفقاً للملاحظات أعلاه وإعادة تقديمه مجدداً. نتطلع إلى نشر إعلانك قريباً.</p>
<div class='btn-wrap'><a href='{{site_url}}' class='btn'>تعديل الإعلان</a></div>
"""
    en_body = """
<p>Hello <strong>{{user_name}}</strong>,</p>
<p>We regret to inform you that your ad <strong>"{{ad_title}}"</strong> was not approved at this time.</p>
<div class='warn-box' style='border-left:4px solid #ff8534;border-right:none;'>
  <strong>Reason:</strong> {{reject_reason}}
</div>
<p>You can edit your ad based on the notes above and resubmit it. We look forward to publishing it soon.</p>
<div class='btn-wrap'><a href='{{site_url}}' class='btn'>Edit Your Ad</a></div>
"""
    ar, en = _html("إعلانك بحاجة إلى مراجعة", "يرجى الاطلاع على التفاصيل", "Ad Needs Review", "Please see the details below", ar_body, en_body)
    return dict(
        key="ad_rejected", name="Ad Rejected Email", name_ar="بريد رفض الإعلان",
        subject="{{site_name}} - إعلانك بحاجة إلى مراجعة", subject_ar="{{site_name}} - إعلانك بحاجة إلى مراجعة",
        body=en, body_ar=ar,
        available_variables="{{user_name}}\n{{site_name}}\n{{ad_title}}\n{{reject_reason}}\n{{site_url}}",
    )


def _order_created():
    ar_body = """
<p>مرحباً <strong>{{user_name}}</strong>،</p>
<p>شكراً لطلبك! تم استلام طلبك رقم <strong>#{{order_number}}</strong> بنجاح وهو قيد المعالجة.</p>
<div class='info-box'>
  <table>
    <tr><td class='lbl'>رقم الطلب</td><td><strong>#{{order_number}}</strong></td></tr>
    <tr><td class='lbl'>الإجمالي</td><td><strong>{{order_total}}</strong></td></tr>
    <tr><td class='lbl'>الحالة</td><td><span style='color:#059669;font-weight:600;'>قيد المعالجة</span></td></tr>
  </table>
</div>
<p>سنُخطرك بتحديثات حالة طلبك فور توفرها.</p>
<div class='btn-wrap'><a href='{{site_url}}' class='btn'>تتبع طلبك</a></div>
"""
    en_body = """
<p>Hello <strong>{{user_name}}</strong>,</p>
<p>Thank you for your order! Order <strong>#{{order_number}}</strong> has been received and is being processed.</p>
<div class='info-box' style='border-left:4px solid #6b4c7a;border-right:none;'>
  <table>
    <tr><td class='lbl'>Order Number</td><td><strong>#{{order_number}}</strong></td></tr>
    <tr><td class='lbl'>Total</td><td><strong>{{order_total}}</strong></td></tr>
    <tr><td class='lbl'>Status</td><td><span style='color:#059669;font-weight:600;'>Processing</span></td></tr>
  </table>
</div>
<p>We'll notify you as soon as your order status is updated.</p>
<div class='btn-wrap'><a href='{{site_url}}' class='btn'>Track Your Order</a></div>
"""
    ar, en = _html("تأكيد استلام الطلب", "تم استلام طلبك بنجاح", "Order Confirmed", "Your order has been received", ar_body, en_body)
    return dict(
        key="order_created", name="Order Created Email", name_ar="تأكيد الطلب",
        subject="{{site_name}} - تأكيد الطلب #{{order_number}}", subject_ar="{{site_name}} - تأكيد طلبك #{{order_number}}",
        body=en, body_ar=ar,
        available_variables="{{user_name}}\n{{site_name}}\n{{order_number}}\n{{order_total}}\n{{site_url}}",
    )


def _order_status_update():
    ar_body = """
<p>مرحباً <strong>{{user_name}}</strong>،</p>
<p>تم تحديث حالة طلبك رقم <strong>#{{order_number}}</strong>.</p>
<div class='info-box'>
  <table>
    <tr><td class='lbl'>رقم الطلب</td><td><strong>#{{order_number}}</strong></td></tr>
    <tr><td class='lbl'>الحالة الجديدة</td><td><strong style='color:#6b4c7a;'>{{order_status}}</strong></td></tr>
  </table>
</div>
<div class='btn-wrap'><a href='{{site_url}}' class='btn'>عرض تفاصيل الطلب</a></div>
"""
    en_body = """
<p>Hello <strong>{{user_name}}</strong>,</p>
<p>Your order <strong>#{{order_number}}</strong> status has been updated.</p>
<div class='info-box' style='border-left:4px solid #6b4c7a;border-right:none;'>
  <table>
    <tr><td class='lbl'>Order Number</td><td><strong>#{{order_number}}</strong></td></tr>
    <tr><td class='lbl'>New Status</td><td><strong style='color:#6b4c7a;'>{{order_status}}</strong></td></tr>
  </table>
</div>
<div class='btn-wrap'><a href='{{site_url}}' class='btn'>View Order Details</a></div>
"""
    ar, en = _html("تحديث حالة طلبك", "تم تحديث الحالة", "Order Status Update", "Status has been updated", ar_body, en_body)
    return dict(
        key="order_status_update", name="Order Status Update Email", name_ar="تحديث حالة الطلب",
        subject="{{site_name}} - تحديث حالة الطلب #{{order_number}}", subject_ar="{{site_name}} - تحديث حالة طلبك #{{order_number}}",
        body=en, body_ar=ar,
        available_variables="{{user_name}}\n{{site_name}}\n{{order_number}}\n{{order_status}}\n{{site_url}}",
    )


def _package_activated():
    ar_body = """
<p>مرحباً <strong>{{user_name}}</strong>،</p>
<p>تم تفعيل باقتك بنجاح! يمكنك الآن الاستفادة الكاملة من مميزاتها.</p>
<div class='success-box'>
  <table>
    <tr><td class='lbl'>الباقة</td><td><strong>{{package_name}}</strong></td></tr>
    <tr><td class='lbl'>عدد الإعلانات</td><td><strong>{{ad_count}} إعلان</strong></td></tr>
    <tr><td class='lbl'>المبلغ المدفوع</td><td><strong>{{payment_amount}}</strong></td></tr>
  </table>
</div>
<div class='btn-wrap'><a href='{{site_url}}' class='btn'>انشر إعلانك الآن</a></div>
"""
    en_body = """
<p>Hello <strong>{{user_name}}</strong>,</p>
<p>Your package has been successfully activated! You can now fully enjoy its benefits.</p>
<div class='success-box' style='border-left:4px solid #059669;border-right:none;'>
  <table>
    <tr><td class='lbl'>Package</td><td><strong>{{package_name}}</strong></td></tr>
    <tr><td class='lbl'>Ad Count</td><td><strong>{{ad_count}} ads</strong></td></tr>
    <tr><td class='lbl'>Amount Paid</td><td><strong>{{payment_amount}}</strong></td></tr>
  </table>
</div>
<div class='btn-wrap'><a href='{{site_url}}' class='btn'>Post Your Ad Now</a></div>
"""
    ar, en = _html("تم تفعيل باقتك! 🎉", "استمتع بمميزاتها الآن", "Package Activated! 🎉", "Enjoy your benefits now", ar_body, en_body)
    return dict(
        key="package_activated", name="Package Activated Email", name_ar="تفعيل الباقة",
        subject="{{site_name}} - تم تفعيل باقة {{package_name}}", subject_ar="{{site_name}} - تم تفعيل باقتك {{package_name}}",
        body=en, body_ar=ar,
        available_variables="{{user_name}}\n{{site_name}}\n{{package_name}}\n{{ad_count}}\n{{payment_amount}}\n{{site_url}}",
    )


def _saved_search_notification():
    ar_body = """
<p>مرحباً <strong>{{user_name}}</strong>،</p>
<p>توجد إعلانات جديدة تطابق بحثك المحفوظ <strong>«{{search_name}}»</strong>.</p>
<div class='info-box'>
  تفقد النتائج الجديدة قبل أن تفوتك!
</div>
<div class='btn-wrap'><a href='{{search_url}}' class='btn'>عرض الإعلانات الجديدة</a></div>
"""
    en_body = """
<p>Hello <strong>{{user_name}}</strong>,</p>
<p>New listings match your saved search <strong>"{{search_name}}"</strong>.</p>
<div class='info-box' style='border-left:4px solid #6b4c7a;border-right:none;'>
  Check the new results before they're gone!
</div>
<div class='btn-wrap'><a href='{{search_url}}' class='btn'>View New Listings</a></div>
"""
    ar, en = _html("إعلانات جديدة تناسبك!", "تطابق بحثك المحفوظ", "New Listings Match Your Search!", "Matching your saved search", ar_body, en_body)
    return dict(
        key="saved_search_notification", name="Saved Search Notification", name_ar="إشعار البحث المحفوظ",
        subject="{{site_name}} - إعلانات جديدة لـ «{{search_name}}»", subject_ar="{{site_name}} - إعلانات جديدة لبحثك «{{search_name}}»",
        body=en, body_ar=ar,
        available_variables="{{user_name}}\n{{site_name}}\n{{search_name}}\n{{search_url}}",
    )


def _newsletter_confirmation():
    ar_body = """
<p>مرحباً،</p>
<p>شكراً لاشتراكك في النشرة البريدية لـ <strong>{{site_name}}</strong>! ستصلك أحدث الإعلانات والعروض مباشرةً إلى بريدك.</p>
<div class='success-box'>
  ✅ اشتراكك فعّال الآن. نتطلع إلى مشاركتك بكل جديد!
</div>
<div class='btn-wrap'><a href='{{site_url}}' class='btn'>استكشف الإعلانات</a></div>
<hr class='divider'>
<p style='font-size:13px;color:#999;text-align:center;'>إذا لم تشترك أنت، <a href='{{unsubscribe_url}}' style='color:#6b4c7a;'>اضغط هنا لإلغاء الاشتراك</a>.</p>
"""
    en_body = """
<p>Hello,</p>
<p>Thank you for subscribing to the <strong>{{site_name}}</strong> newsletter! You'll receive the latest ads and offers directly in your inbox.</p>
<div class='success-box' style='border-left:4px solid #059669;border-right:none;'>
  ✅ Your subscription is now active. We look forward to keeping you informed!
</div>
<div class='btn-wrap'><a href='{{site_url}}' class='btn'>Explore Listings</a></div>
<hr class='divider'>
<p style='font-size:13px;color:#999;text-align:center;'>If you didn't subscribe, <a href='{{unsubscribe_url}}' style='color:#6b4c7a;'>click here to unsubscribe</a>.</p>
"""
    ar, en = _html("تم الاشتراك بنجاح!", "مرحباً بك في نشرتنا", "Subscribed Successfully!", "Welcome to our newsletter", ar_body, en_body)
    return dict(
        key="newsletter_confirmation", name="Newsletter Confirmation", name_ar="تأكيد الاشتراك في النشرة البريدية",
        subject="{{site_name}} - تأكيد اشتراكك في النشرة البريدية", subject_ar="{{site_name}} - تأكيد اشتراكك في النشرة البريدية",
        body=en, body_ar=ar,
        available_variables="{{site_name}}\n{{site_url}}\n{{unsubscribe_url}}",
    )


def _contact_form():
    ar_body = """
<p>تم استلام رسالة جديدة عبر نموذج التواصل.</p>
<div class='info-box'>
  <table>
    <tr><td class='lbl'>المرسل</td><td><strong>{{sender_name}}</strong></td></tr>
    <tr><td class='lbl'>البريد الإلكتروني</td><td><a href='mailto:{{sender_email}}' style='color:#6b4c7a;'>{{sender_email}}</a></td></tr>
    <tr><td class='lbl'>الموضوع</td><td>{{subject_text}}</td></tr>
  </table>
</div>
<p><strong>الرسالة:</strong></p>
<div style='background:#f9f9f9;border:1px solid #eee;border-radius:6px;padding:16px;margin-top:8px;'>
  {{message}}
</div>
"""
    en_body = """
<p>A new message was received via the contact form.</p>
<div class='info-box' style='border-left:4px solid #6b4c7a;border-right:none;'>
  <table>
    <tr><td class='lbl'>Sender</td><td><strong>{{sender_name}}</strong></td></tr>
    <tr><td class='lbl'>Email</td><td><a href='mailto:{{sender_email}}' style='color:#6b4c7a;'>{{sender_email}}</a></td></tr>
    <tr><td class='lbl'>Subject</td><td>{{subject_text}}</td></tr>
  </table>
</div>
<p><strong>Message:</strong></p>
<div style='background:#f9f9f9;border:1px solid #eee;border-radius:6px;padding:16px;margin-top:8px;'>
  {{message}}
</div>
"""
    ar, en = _html("رسالة جديدة من نموذج التواصل", "تحقق من التفاصيل أدناه", "New Contact Form Message", "Check the details below", ar_body, en_body)
    return dict(
        key="contact_form", name="Contact Form Email", name_ar="رسالة نموذج التواصل",
        subject="{{site_name}} - رسالة جديدة من {{sender_name}}", subject_ar="{{site_name}} - رسالة جديدة من {{sender_name}}",
        body=en, body_ar=ar,
        available_variables="{{site_name}}\n{{sender_name}}\n{{sender_email}}\n{{subject_text}}\n{{message}}",
    )


ALL_TEMPLATES = [
    _welcome,
    _password_reset,
    _email_verification,
    _otp_verification,
    _ad_approved,
    _ad_rejected,
    _order_created,
    _order_status_update,
    _package_activated,
    _saved_search_notification,
    _newsletter_confirmation,
    _contact_form,
]


class Command(BaseCommand):
    help = (
        "Seed EmailTemplate with default bilingual (AR/EN) content for all predefined keys.\n"
        "  --overwrite  Replace body/subject of existing templates\n"
        "  --key KEY    Seed only the specified template key"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--overwrite",
            action="store_true",
            default=False,
            help="Overwrite existing templates (default: skip existing)",
        )
        parser.add_argument(
            "--key",
            type=str,
            default=None,
            help="Seed only a specific template key",
        )

    def handle(self, *args, **options):
        from main.models import EmailTemplate

        overwrite = options["overwrite"]
        only_key = options.get("key")

        created_count = 0
        updated_count = 0
        skipped_count = 0

        templates_to_seed = [fn() for fn in ALL_TEMPLATES]

        if only_key:
            templates_to_seed = [t for t in templates_to_seed if t["key"] == only_key]
            if not templates_to_seed:
                self.stdout.write(self.style.ERROR(f"No template found for key: '{only_key}'"))
                self.stdout.write("Available keys: " + ", ".join(fn()["key"] for fn in ALL_TEMPLATES))
                return

        for data in templates_to_seed:
            key = data.pop("key")
            existing = EmailTemplate.objects.filter(key=key).first()

            if existing:
                if overwrite:
                    for field, value in data.items():
                        setattr(existing, field, value)
                    existing.save()
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f"  ↻  Updated : {key}"))
                else:
                    skipped_count += 1
                    self.stdout.write(f"  –  Skipped : {key}  (already exists, use --overwrite to replace)")
            else:
                EmailTemplate.objects.create(key=key, **data)
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓  Created : {key}"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Done — created: {created_count}, updated: {updated_count}, skipped: {skipped_count}"
        ))
