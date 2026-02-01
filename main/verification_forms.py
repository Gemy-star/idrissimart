# main/verification_forms.py
"""Forms for user verification system"""

from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import UserVerificationRequest


class UserVerificationRequestForm(forms.ModelForm):
    """Form for users to request account verification"""

    class Meta:
        model = UserVerificationRequest
        fields = ["document_type", "document_file", "notes"]
        widgets = {
            "document_type": forms.Select(
                attrs={
                    "class": "form-select",
                    "required": True,
                }
            ),
            "document_file": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*,.pdf",
                    "required": True,
                }
            ),
            "notes": CKEditor5Widget(
                attrs={
                    "class": "form-control django_ckeditor_5",
                    "dir": "rtl",
                },
                config_name="extends",
            ),
        }
        labels = {
            "document_type": _("نوع الوثيقة"),
            "document_file": _("رفع الوثيقة"),
            "notes": _("ملاحظات إضافية"),
        }
        help_texts = {
            "document_file": _("يرجى رفع صورة واضحة للوثيقة (PNG, JPG, PDF - حجم أقصى 5MB)"),
            "notes": _("يمكنك إضافة أي معلومات إضافية تساعد في مراجعة طلبك"),
        }

    def clean_document_file(self):
        """Validate document file size and type"""
        file = self.cleaned_data.get("document_file")

        if file:
            # Check file size (max 5MB)
            if file.size > 5 * 1024 * 1024:
                raise ValidationError(
                    _("حجم الملف كبير جداً. الحد الأقصى المسموح 5 ميجابايت.")
                )

            # Check file type
            allowed_types = [
                "image/jpeg",
                "image/jpg",
                "image/png",
                "image/gif",
                "application/pdf",
            ]
            if file.content_type not in allowed_types:
                raise ValidationError(
                    _("نوع الملف غير مدعوم. يرجى رفع صورة (JPG, PNG, GIF) أو PDF.")
                )

        return file

    def clean(self):
        """Additional validation"""
        cleaned_data = super().clean()
        document_type = cleaned_data.get("document_type")
        document_file = cleaned_data.get("document_file")

        if document_type and not document_file:
            raise ValidationError(
                _("يرجى رفع الوثيقة المطلوبة لإكمال طلب التوثيق.")
            )

        return cleaned_data
