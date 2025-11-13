# main/forms.py
from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from .models import (
    AdImage,
    ClassifiedAd,
    ContactMessage,
    User,
    Category,
    AdFeaturePrice,
)


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

    condition = forms.ChoiceField(  # This seems to be a remnant of a previous approach, it's better to handle it dynamically.
        required=False,
        choices=[
            ("", _("---------")),
            ("new", _("جديد")),
            ("used", "مستعمل - كالجديد"),
            ("used_good", "مستعمل - جيد"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    # Mobile number field for contact
    mobile_number = forms.CharField(
        max_length=20,
        required=True,
        label=_("رقم الجوال"),
        help_text=_("رقم الجوال للتواصل (يجب التحقق منه)"),
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": _("مثال: 0501234567"),
            "id": "mobile_number"
        })
    )
    # The 'brand' field is also better handled dynamically.

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
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Initialize mobile number from user's profile
        if self.user and self.user.mobile:
            self.fields['mobile_number'].initial = self.user.mobile
        
        category = None
        if "category" in self.data:
            try:
                category = Category.objects.get(pk=self.data.get("category"))
            except (Category.DoesNotExist, ValueError):
                pass
        elif self.instance and self.instance.pk:
            category = self.instance.category

        if category:
            self.add_custom_fields(category)

        if self.instance and self.instance.pk and self.instance.custom_fields:
            for field_name, value in self.instance.custom_fields.items():
                if field_name in self.fields:
                    self.fields[field_name].initial = value

    def add_custom_fields(self, category):
        """
        Adds form fields based on the category's custom_field_schema, including validation.
        """
        schema = category.custom_field_schema or []

        for field_schema in schema:
            field_name = field_schema.get("name")
            if not field_name:
                continue

            field_label = field_schema.get("label", field_name)
            field_type = field_schema.get("type", "text")
            required = field_schema.get("required", False)
            options = field_schema.get("options", [])
            validation_rules = field_schema.get("validation", {})

            field_kwargs = {
                "label": field_label,
                "required": required,
            }
            widget_attrs = {"class": "form-control"}

            if field_type == "select":
                field_kwargs["choices"] = [("", "---------")] + [
                    (opt, opt) for opt in options
                ]
                widget_attrs["class"] = "form-select"
                self.fields[field_name] = forms.ChoiceField(
                    **field_kwargs, widget=forms.Select(attrs=widget_attrs)
                )

            elif field_type == "checkbox":
                widget_attrs["class"] = "form-check-input"
                self.fields[field_name] = forms.BooleanField(
                    **field_kwargs, widget=forms.CheckboxInput(attrs=widget_attrs)
                )

            elif field_type == "date":
                widget_attrs["type"] = "date"
                self.fields[field_name] = forms.DateField(
                    **field_kwargs, widget=forms.DateInput(attrs=widget_attrs)
                )

            elif field_type == "number":
                field_kwargs.update(
                    {
                        "min_value": validation_rules.get("min_value"),
                        "max_value": validation_rules.get("max_value"),
                    }
                )
                widget_attrs.update(
                    {
                        "min": validation_rules.get("min_value"),
                        "max": validation_rules.get("max_value"),
                    }
                )
                self.fields[field_name] = forms.IntegerField(
                    **field_kwargs, widget=forms.NumberInput(attrs=widget_attrs)
                )

            else:  # Default to text
                field_kwargs.update(
                    {
                        "min_length": validation_rules.get("min_length"),
                        "max_length": validation_rules.get("max_length"),
                    }
                )
                widget_attrs.update(
                    {
                        "minlength": validation_rules.get("min_length"),
                        "maxlength": validation_rules.get("max_length"),
                    }
                )
                self.fields[field_name] = forms.CharField(
                    **field_kwargs, widget=forms.TextInput(attrs=widget_attrs)
                )

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Ensure custom_fields is a dict
        if not isinstance(instance.custom_fields, dict):
            instance.custom_fields = {}

        # Gather custom field data
        if instance.category and instance.category.custom_field_schema:
            schema = instance.category.custom_field_schema or []
            custom_field_keys = [
                field.get("name") for field in schema if field.get("name")
            ]

            for key in custom_field_keys:
                if key in self.cleaned_data:
                    instance.custom_fields[key] = self.cleaned_data[key]

        if commit:
            instance.save()
        return instance
    
    def clean_mobile_number(self):
        """Validate mobile number format"""
        mobile_number = self.cleaned_data.get('mobile_number')
        if mobile_number:
            # Remove spaces and special characters
            mobile_number = ''.join(filter(str.isdigit, mobile_number))
            
            # Check if it's a valid Saudi mobile number
            if not mobile_number.startswith('05') or len(mobile_number) != 10:
                raise forms.ValidationError(_('رقم الجوال يجب أن يبدأ بـ 05 ويتكون من 10 أرقام'))
        
        return mobile_number
    
    def clean(self):
        """Validate that mobile number is verified for new ads"""
        cleaned_data = super().clean()
        mobile_number = cleaned_data.get('mobile_number')
        
        if mobile_number and self.user:
            # Check if this is a new ad (not editing existing one)
            if not self.instance.pk:
                # Check if mobile verification is required
                from .services import MobileVerificationService
                verification_service = MobileVerificationService()
                required, message = verification_service.check_mobile_verification_required(
                    self.user, mobile_number
                )
                
                if required:
                    raise forms.ValidationError(_('يجب التحقق من رقم الجوال قبل نشر الإعلان'))
        
        return cleaned_data


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


class SimpleEnhancedAdForm(forms.ModelForm):
    """
    نموذج مبسط لإنشاء الإعلانات المحسنة
    Simplified form for enhanced classified ads
    """

    # حقول التواصل
    contact_phone = forms.CharField(
        label=_("رقم الهاتف"),
        widget=forms.TextInput(
            attrs={"class": "form-control rtl", "placeholder": _("مثال: 05xxxxxxxx")}
        ),
        max_length=20,
        required=False,
    )

    contact_whatsapp = forms.CharField(
        label=_("واتساب"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control rtl",
                "placeholder": _("رقم الواتساب مع كود الدولة"),
            }
        ),
        max_length=20,
        required=False,
    )

    # خيارات التوصيل
    delivery_available = forms.BooleanField(
        label=_("يتوفر توصيل"), required=False, help_text=_("هل تقدم خدمة التوصيل؟")
    )

    # معلومات الشروط والأحكام
    accept_terms = forms.BooleanField(
        label=_("أوافق على شروط الاستخدام"), required=True
    )

    class Meta:
        model = ClassifiedAd
        fields = [
            "title",
            "description",
            "price",
            "category",
            "city",
            "address",
            "is_negotiable",
            "is_delivery_available",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control rtl", "placeholder": _("عنوان الإعلان")}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control rtl",
                    "rows": 5,
                    "placeholder": _("وصف تفصيلي للإعلان..."),
                }
            ),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": _("السعر بالريال")}
            ),
            "category": forms.Select(attrs={"class": "form-control select2"}),
            "subcategory": forms.Select(
                attrs={"class": "form-control select2", "disabled": True}
            ),
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop("user", None)  # إزالة المعامل غير المستخدم
        super().__init__(*args, **kwargs)
