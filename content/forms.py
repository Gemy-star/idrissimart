from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import Comment, PaymentMethodConfig
from .site_config import AboutPage


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
