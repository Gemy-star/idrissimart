# main/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """Contact form for user inquiries"""

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("أدخل اسمك الكامل"),
                    "dir": "rtl",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("أدخل بريدك الإلكتروني"),
                    "dir": "ltr",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("أدخل رقم هاتفك"),
                    "dir": "ltr",
                }
            ),
            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("موضوع الرسالة"),
                    "dir": "rtl",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": _("اكتب رسالتك هنا..."),
                    "rows": 5,
                    "dir": "rtl",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        """Save the contact message with user if available"""
        contact_message = super().save(commit=False)
        if self.user and self.user.is_authenticated:
            contact_message.user = self.user
        if commit:
            contact_message.save()
        return contact_message
