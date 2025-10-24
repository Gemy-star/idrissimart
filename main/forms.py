# main/forms.py
from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from .models import AdImage, ClassifiedAd, ContactMessage


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


class ClassifiedAdForm(forms.ModelForm):
    """Form for creating and editing classified ads."""

    brand = forms.CharField(
        label=_("الماركة / الشركة المصنعة"),
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    condition = forms.ChoiceField(
        label=_("حالة المنتج"),
        required=False,
        choices=[
            ("", _("---------")),
            ("new", _("جديد")),
            ("used", "مستعمل - كالجديد"),
            ("used_good", "مستعمل - جيد"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = ClassifiedAd
        fields = [
            "category",
            "title",
            "description",
            "price",
            "is_negotiable",
            "country",
            "city",
            "address",
            "is_cart_enabled",
            "is_delivery_available",
            "video_url",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "video_url": forms.URLInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.custom_fields:
            self.fields["brand"].initial = self.instance.custom_fields.get("brand")
            self.fields["condition"].initial = self.instance.custom_fields.get(
                "condition"
            )

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.custom_fields["brand"] = self.cleaned_data.get("brand")
        instance.custom_fields["condition"] = self.cleaned_data.get("condition")
        if commit:
            instance.save()
        return instance


AdImageFormSet = inlineformset_factory(
    ClassifiedAd,
    AdImage,
    fields=("image",),
    extra=5,  # Number of extra empty forms to display
    can_delete=True,
    max_num=5,  # Maximum number of images
)
