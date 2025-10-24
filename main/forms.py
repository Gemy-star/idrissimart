# main/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from .models import AdImage, ClassifiedAd, ContactMessage, User


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


class RegistrationForm(forms.Form):
    """
    A form for user registration, handling validation for different profile types.
    """

    username = forms.CharField(
        label=_("اسم المستخدم"),
        min_length=3,
        widget=forms.TextInput(attrs={"placeholder": _("اسم المستخدم")}),
    )
    email = forms.EmailField(
        label=_("البريد الإلكتروني"),
        widget=forms.EmailInput(attrs={"placeholder": _("البريد الإلكتروني")}),
    )
    password = forms.CharField(
        label=_("كلمة المرور"),
        min_length=8,
        widget=forms.PasswordInput(attrs={"placeholder": _("كلمة المرور")}),
    )
    password2 = forms.CharField(
        label=_("تأكيد كلمة المرور"),
        widget=forms.PasswordInput(attrs={"placeholder": _("تأكيد كلمة المرور")}),
    )
    first_name = forms.CharField(label=_("الاسم الأول"), required=False)
    last_name = forms.CharField(label=_("الاسم الأخير"), required=False)
    phone = forms.CharField(label=_("الهاتف"), required=False)
    profile_type = forms.ChoiceField(
        label=_("نوع الحساب"),
        choices=User.ProfileType.choices,
        initial=User.ProfileType.DEFAULT,
    )
    terms_accepted = forms.BooleanField(
        label=_("أوافق على الشروط والأحكام"),
        required=True,
        error_messages={"required": _("يجب الموافقة على الشروط والأحكام")},
    )

    # Fields for service provider
    specialization = forms.CharField(
        label=_("التخصص"),
        required=False,
        widget=forms.TextInput(attrs={"class": "service-field"}),
    )
    years_of_experience = forms.IntegerField(
        label=_("سنوات الخبرة"),
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "service-field"}),
    )

    # Fields for merchant/educational
    company_name = forms.CharField(
        label=_("اسم الشركة"),
        required=False,
        widget=forms.TextInput(attrs={"class": "merchant-field educational-field"}),
    )
    company_name_ar = forms.CharField(
        label=_("اسم الشركة بالعربية"),
        required=False,
        widget=forms.TextInput(attrs={"class": "merchant-field educational-field"}),
    )
    commercial_register = forms.CharField(
        label=_("السجل التجاري"),
        required=False,
        widget=forms.TextInput(attrs={"class": "merchant-field"}),
    )
    tax_number = forms.CharField(
        label=_("الرقم الضريبي"),
        required=False,
        widget=forms.TextInput(attrs={"class": "merchant-field"}),
    )

    def clean_username(self):
        username = self.cleaned_data.get("username").lower()
        if User.objects.filter(username=username).exists():
            raise ValidationError(_("اسم المستخدم موجود بالفعل"))
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email").lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("البريد الإلكتروني مسجل بالفعل"))
        return email

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise ValidationError(_("كلمات المرور غير متطابقة"))
        return password2

    def clean(self):
        cleaned_data = super().clean()
        profile_type = cleaned_data.get("profile_type")

        if profile_type == "service" and not cleaned_data.get("specialization"):
            self.add_error("specialization", _("التخصص مطلوب لمقدمي الخدمات."))

        if profile_type == "merchant" and not cleaned_data.get("company_name"):
            self.add_error("company_name", _("اسم الشركة مطلوب للتجار."))

        return cleaned_data
