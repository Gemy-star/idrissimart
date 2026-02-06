from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import Comment, PaymentMethodConfig
from .site_config import AboutPage, SiteConfiguration, TermsPage, PrivacyPage


class CommentForm(forms.ModelForm):
    """
    Comment form for public pages - uses simple textarea instead of CKEditor.
    CKEditor is only used in admin dashboard pages.
    """

    parent_id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Comment
        fields = ("body", "parent_id")
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "اكتب تعليقك هنا...",
                }
            ),
        }


class AboutPageForm(forms.ModelForm):
    """Form for editing About Page content in admin dashboard"""

    class Meta:
        model = AboutPage
        fields = [
            "title",
            "title_ar",
            "content",
            "content_ar",
            "mission",
            "mission_ar",
            "vision",
            "vision_ar",
            "values",
            "values_ar",
            "featured_image",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter title in English",
                }
            ),
            "title_ar": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "أدخل العنوان بالعربية",
                    "dir": "rtl",
                }
            ),
            "content": CKEditor5Widget(
                config_name="admin", attrs={"class": "django_ckeditor_5"}
            ),
            "content_ar": CKEditor5Widget(
                config_name="admin", attrs={"class": "django_ckeditor_5"}
            ),
            "mission": CKEditor5Widget(
                config_name="admin", attrs={"class": "django_ckeditor_5"}
            ),
            "mission_ar": CKEditor5Widget(
                config_name="admin", attrs={"class": "django_ckeditor_5"}
            ),
            "vision": CKEditor5Widget(
                config_name="admin", attrs={"class": "django_ckeditor_5"}
            ),
            "vision_ar": CKEditor5Widget(
                config_name="admin", attrs={"class": "django_ckeditor_5"}
            ),
            "values": CKEditor5Widget(
                config_name="admin", attrs={"class": "django_ckeditor_5"}
            ),
            "values_ar": CKEditor5Widget(
                config_name="admin", attrs={"class": "django_ckeditor_5"}
            ),
            "featured_image": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
        }
        labels = {
            "title": "Title (English)",
            "title_ar": "العنوان (عربي)",
            "content": "Content (English)",
            "content_ar": "المحتوى (عربي)",
            "mission": "Mission (English)",
            "mission_ar": "رسالتنا (عربي)",
            "vision": "Vision (English)",
            "vision_ar": "رؤيتنا (عربي)",
            "values": "Values (English)",
            "values_ar": "قيمنا (عربي)",
            "featured_image": "Featured Image / الصورة المميزة",
        }


class PaymentMethodConfigForm(forms.ModelForm):
    """Form for managing payment method configurations per context"""

    class Meta:
        model = PaymentMethodConfig
        fields = [
            "context",
            "visa_enabled",
            "paypal_enabled",
            "wallet_enabled",
            "instapay_enabled",
            "cod_enabled",
            "partial_enabled",
            "cod_requires_deposit",
            "cod_deposit_type",
            "cod_deposit_amount",
            "cod_deposit_percentage",
            "notes",
            "is_active",
        ]
        widgets = {
            "context": forms.Select(
                attrs={"class": "form-select", "disabled": "disabled"}
            ),
            "visa_enabled": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "paypal_enabled": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "wallet_enabled": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "instapay_enabled": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "cod_enabled": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "partial_enabled": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "cod_requires_deposit": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "cod_deposit_type": forms.Select(attrs={"class": "form-select"}),
            "cod_deposit_amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "cod_deposit_percentage": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make context readonly for existing instances
        if self.instance and self.instance.pk:
            self.fields["context"].disabled = True


class SiteConfigurationForm(forms.ModelForm):
    """Form for editing Site Configuration settings in admin dashboard"""

    class Meta:
        model = SiteConfiguration
        fields = [
            "meta_keywords",
            "meta_keywords_ar",
            "footer_text",
            "footer_text_ar",
            "copyright_text",
            "logo",
            "logo_light",
            "logo_dark",
            "logo_mini",
            "require_email_verification",
            "require_phone_verification",
            "require_verification_for_services",
            "require_verification_for_free_package",
            "verification_services_message",
            "verification_services_message_ar",
            "allow_online_payment",
            "allow_offline_payment",
            "instapay_qr_code",
            "instapay_phone",
            "wallet_payment_link",
            "wallet_phone",
            "offline_payment_instructions",
            "offline_payment_instructions_ar",
            "ad_base_fee",
            "featured_ad_price",
            "urgent_ad_price",
            "pinned_ad_price",
            "cart_service_fee_type",
            "cart_service_fixed_fee",
            "cart_service_percentage",
            "cart_service_instructions",
            "deleted_ads_retention_days",
            "expired_ads_retention_days",
            "show_deleted_ads_to_publisher",
            "show_expired_ads_to_publisher",
            "buyer_safety_notes_enabled",
            "buyer_safety_notes",
            "buyer_safety_notes_ar",
            "buyer_safety_notes_title",
            "buyer_safety_notes_title_ar",
        ]
        widgets = {
            "meta_keywords": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "keyword1, keyword2, keyword3",
                }
            ),
            "meta_keywords_ar": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "كلمة1, كلمة2, كلمة3",
                    "dir": "rtl",
                }
            ),
            "footer_text": CKEditor5Widget(
                config_name="admin", attrs={"class": "django_ckeditor_5"}
            ),
            "footer_text_ar": CKEditor5Widget(
                config_name="admin", attrs={"class": "django_ckeditor_5"}
            ),
            "copyright_text": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "© 2024 Your Site. All rights reserved.",
                    "dir": "rtl",
                }
            ),
            "logo": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "logo_light": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "logo_dark": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "logo_mini": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "require_email_verification": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "require_phone_verification": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "require_verification_for_services": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "require_verification_for_free_package": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "verification_services_message": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "verification_services_message_ar": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "dir": "rtl"}
            ),
            "allow_online_payment": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "allow_offline_payment": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "instapay_qr_code": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "instapay_phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+20 123 456 7890"}
            ),
            "wallet_payment_link": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "https://..."}
            ),
            "wallet_phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+20 123 456 7890"}
            ),
            "offline_payment_instructions": forms.Textarea(
                attrs={"class": "form-control", "rows": 4}
            ),
            "offline_payment_instructions_ar": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "dir": "rtl"}
            ),
            "ad_base_fee": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "featured_ad_price": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "urgent_ad_price": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "pinned_ad_price": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "cart_service_fee_type": forms.Select(attrs={"class": "form-select"}),
            "cart_service_fixed_fee": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "cart_service_percentage": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "cart_service_instructions": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "dir": "rtl"}
            ),
            "deleted_ads_retention_days": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "expired_ads_retention_days": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "show_deleted_ads_to_publisher": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "show_expired_ads_to_publisher": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "buyer_safety_notes_enabled": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "buyer_safety_notes": CKEditor5Widget(
                config_name="admin", attrs={"class": "django_ckeditor_5"}
            ),
            "buyer_safety_notes_ar": CKEditor5Widget(
                config_name="admin", attrs={"class": "django_ckeditor_5"}
            ),
            "buyer_safety_notes_title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Safety Tips"}
            ),
            "buyer_safety_notes_title_ar": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نصائح الأمان",
                    "dir": "rtl",
                }
            ),
        }


class TermsPageForm(forms.ModelForm):
    """Form for editing Terms and Conditions page"""

    class Meta:
        model = TermsPage
        fields = ["title", "title_ar", "content", "content_ar"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Terms and Conditions"}
            ),
            "title_ar": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "الشروط والأحكام",
                    "dir": "rtl",
                }
            ),
            "content": CKEditor5Widget(
                config_name="admin", attrs={"class": "django_ckeditor_5"}
            ),
            "content_ar": CKEditor5Widget(
                config_name="admin", attrs={"class": "django_ckeditor_5"}
            ),
        }


class PrivacyPageForm(forms.ModelForm):
    """Form for editing Privacy Policy page"""

    class Meta:
        model = PrivacyPage
        fields = ["title", "title_ar", "content", "content_ar"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Privacy Policy"}
            ),
            "title_ar": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "سياسة الخصوصية",
                    "dir": "rtl",
                }
            ),
            "content": CKEditor5Widget(
                config_name="admin", attrs={"class": "django_ckeditor_5"}
            ),
            "content_ar": CKEditor5Widget(
                config_name="admin", attrs={"class": "django_ckeditor_5"}
            ),
        }
