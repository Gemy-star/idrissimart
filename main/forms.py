# main/forms.py
from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django_ckeditor_5.widgets import CKEditor5Widget
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

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
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("مثال: 0501234567"),
                "id": "mobile_number",
            }
        ),
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
            "description": CKEditor5Widget(config_name="default"),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "video_url": forms.URLInput(attrs={"class": "form-control"}),
        }
        error_messages = {
            "category": {
                "required": _("يجب اختيار القسم المناسب لإعلانك"),
            },
            "title": {
                "required": _("يجب كتابة عنوان للإعلان"),
                "max_length": _("عنوان الإعلان طويل جداً (الحد الأقصى 200 حرف)"),
            },
            "description": {
                "required": _("يجب كتابة وصف تفصيلي للإعلان"),
            },
            "price": {
                "required": _("يجب تحديد السعر"),
                "invalid": _("السعر يجب أن يكون رقماً صحيحاً"),
            },
            "country": {
                "required": _("يجب اختيار الدولة"),
            },
            "city": {
                "required": _("يجب كتابة اسم المدينة"),
            },
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Initialize mobile number from user's profile
        if self.user and self.user.mobile:
            self.fields["mobile_number"].initial = self.user.mobile

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
        Custom fields are rendered by JavaScript, so we set required=False here to avoid
        server-side validation conflicts. Client-side validation is handled in the template.
        """
        schema = category.custom_field_schema or []

        for field_schema in schema:
            field_name = field_schema.get("name")
            if not field_name:
                continue

            field_label = field_schema.get("label", field_name)
            field_type = field_schema.get("type", "text")
            # Custom fields are handled by JavaScript, so we don't enforce required on Django side
            required = False
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
        from main.models import CategoryCustomField

        # Ensure custom_fields is a dict
        if not isinstance(instance.custom_fields, dict):
            instance.custom_fields = {}

        # Gather custom field data from POST data
        if instance.category:
            category_fields = CategoryCustomField.objects.filter(
                category=instance.category,
                is_active=True
            ).select_related('custom_field').order_by('order')

            for cf in category_fields:
                field = cf.custom_field
                field_name = f"custom_{field.name}"

                # Get value from cleaned_data if available, otherwise from data dict
                if field_name in self.cleaned_data:
                    value = self.cleaned_data[field_name]
                elif self.data and field_name in self.data:
                    value = self.data.get(field_name)
                    # Handle checkbox fields
                    if field.field_type == "checkbox":
                        value = value == "on" or value == "true" or value == True
                else:
                    continue

                # Skip empty values for non-required fields
                if not value and value != False and value != 0:
                    continue

                # Convert date objects to strings for JSON serialization
                if hasattr(value, "isoformat"):
                    value = value.isoformat()

                instance.custom_fields[field_name] = value

        if commit:
            instance.save()
        return instance

    def clean_mobile_number(self):
        """Validate mobile number format based on country"""
        mobile_number = self.cleaned_data.get("mobile_number")
        country = self.cleaned_data.get("country") or self.instance.country

        if not mobile_number:
            return mobile_number

        # Remove spaces and special characters
        mobile_number = "".join(filter(str.isdigit, mobile_number))

        # Validation rules per country
        validation_rules = {
            "SA": {  # Saudi Arabia
                "prefix": "05",
                "length": 10,
                "error": _("رقم الجوال السعودي يجب أن يبدأ بـ 05 ويتكون من 10 أرقام"),
            },
            "EG": {  # Egypt
                "prefix": "01",
                "length": 11,
                "error": _("رقم الجوال المصري يجب أن يبدأ بـ 01 ويتكون من 11 رقم"),
            },
            "AE": {  # UAE
                "prefix": "05",
                "length": 10,
                "error": _("رقم الجوال الإماراتي يجب أن يبدأ بـ 05 ويتكون من 10 أرقام"),
            },
            "KW": {  # Kuwait
                "prefix": ("5", "6", "9"),
                "length": 8,
                "error": _("رقم الجوال الكويتي يجب أن يتكون من 8 أرقام"),
            },
            "QA": {  # Qatar
                "prefix": ("3", "5", "6", "7"),
                "length": 8,
                "error": _("رقم الجوال القطري يجب أن يتكون من 8 أرقام"),
            },
            "BH": {  # Bahrain
                "prefix": "3",
                "length": 8,
                "error": _("رقم الجوال البحريني يجب أن يبدأ بـ 3 ويتكون من 8 أرقام"),
            },
            "OM": {  # Oman
                "prefix": ("9", "7"),
                "length": 8,
                "error": _("رقم الجوال العماني يجب أن يتكون من 8 أرقام"),
            },
        }

        # Get country code
        country_code = country.code if country else "SA"

        # Get validation rule for country
        rule = validation_rules.get(country_code)

        if rule:
            # Check length
            if len(mobile_number) != rule["length"]:
                raise forms.ValidationError(rule["error"])

            # Check prefix
            prefix = rule["prefix"]
            if isinstance(prefix, tuple):
                if not mobile_number.startswith(prefix):
                    raise forms.ValidationError(rule["error"])
            else:
                if not mobile_number.startswith(prefix):
                    raise forms.ValidationError(rule["error"])
        else:
            # Generic validation for other countries
            if len(mobile_number) < 8 or len(mobile_number) > 15:
                raise forms.ValidationError(
                    _("رقم الجوال يجب أن يتكون من 8 إلى 15 رقم")
                )

        return mobile_number

    def clean(self):
        """Validate that mobile number is verified for new ads"""
        cleaned_data = super().clean()
        mobile_number = cleaned_data.get("mobile_number")

        if mobile_number and self.user:
            # Check if this is a new ad (not editing existing one)
            if not self.instance.pk:
                # Check if mobile verification is required
                from .services import MobileVerificationService
                from constance import config

                # Only check verification if it's enabled in settings
                verification_enabled = getattr(
                    config, "ENABLE_MOBILE_VERIFICATION", True
                )

                if verification_enabled:
                    verification_service = MobileVerificationService()
                    required, message = (
                        verification_service.check_mobile_verification_required(
                            self.user, mobile_number
                        )
                    )

                    if required:
                        raise forms.ValidationError(
                            _("يجب التحقق من رقم الجوال قبل نشر الإعلان")
                        )

        return cleaned_data


class AdImageForm(forms.ModelForm):
    """Form for individual ad images"""

    class Meta:
        model = AdImage
        fields = ("image",)
        widgets = {
            "image": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make image field optional
        self.fields["image"].required = False


AdImageFormSet = inlineformset_factory(
    ClassifiedAd,
    AdImage,
    form=AdImageForm,
    fields=("image",),
    extra=5,  # Number of extra empty forms to display
    can_delete=True,
    max_num=5,  # Maximum number of images
    validate_min=False,
    validate_max=True,
)


class RegistrationForm(forms.Form):
    """
    A form for user registration, handling validation for different profile types.
    """

    username = forms.CharField(
        label=_("اسم المستخدم"),
        min_length=3,
        widget=forms.TextInput(attrs={"placeholder": _("اسم المستخدم")}),
        error_messages={
            "min_length": _("اسم المستخدم يجب أن يكون 3 أحرف على الأقل."),
            "required": _("اسم المستخدم مطلوب."),
        },
    )
    email = forms.EmailField(
        label=_("البريد الإلكتروني"),
        widget=forms.EmailInput(attrs={"placeholder": _("البريد الإلكتروني")}),
        error_messages={
            "invalid": _("صيغة البريد الإلكتروني غير صحيحة."),
            "required": _("البريد الإلكتروني مطلوب."),
        },
    )
    password = forms.CharField(
        label=_("كلمة المرور"),
        min_length=8,
        widget=forms.PasswordInput(attrs={"placeholder": _("كلمة المرور")}),
        error_messages={
            "min_length": _("كلمة المرور يجب أن تكون 8 أحرف على الأقل."),
            "required": _("كلمة المرور مطلوبة."),
        },
    )
    password2 = forms.CharField(
        label=_("تأكيد كلمة المرور"),
        widget=forms.PasswordInput(attrs={"placeholder": _("تأكيد كلمة المرور")}),
        error_messages={
            "required": _("تأكيد كلمة المرور مطلوب."),
        },
    )
    first_name = forms.CharField(label=_("الاسم الأول"), required=False)
    last_name = forms.CharField(label=_("الاسم الأخير"), required=False)
    country = forms.CharField(
        label=_("الدولة"),
        required=True,
        error_messages={
            "required": _("يجب اختيار الدولة."),
        },
    )
    phone = forms.CharField(
        label=_("رقم الجوال"),
        required=True,
        widget=forms.TextInput(attrs={"placeholder": _("مثال: 0501234567")}),
    )
    phone_verification_code = forms.CharField(
        label=_("رمز التحقق"),
        required=False,
        max_length=6,
        widget=forms.TextInput(attrs={"placeholder": _("أدخل رمز التحقق")}),
    )
    profile_type = forms.ChoiceField(
        label=_("نوع الحساب"),
        choices=[],  # Will be populated in __init__
        initial=User.ProfileType.DEFAULT,
    )
    terms_accepted = forms.BooleanField(
        label=_("أوافق على الشروط والأحكام"),
        required=True,
        error_messages={"required": _("يجب الموافقة على الشروط والأحكام")},
    )

    # Google reCAPTCHA
    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox(
            attrs={
                "data-theme": "light",
                "data-size": "normal",
            }
        ),
        error_messages={
            "required": _("يرجى التحقق من أنك لست روبوت"),
        },
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Build profile type choices based on settings
        from constance import config

        profile_choices = [
            (User.ProfileType.DEFAULT, _("مستخدم افتراضي - Default User")),
            (User.ProfileType.PUBLISHER, _("ناشر - Publisher")),
        ]

        # Add optional profile types based on settings
        if getattr(config, "ENABLE_SERVICE_PROVIDER_REGISTRATION", False):
            profile_choices.append(
                (User.ProfileType.SERVICE, _("خدمي - Service Provider"))
            )

        if getattr(config, "ENABLE_MERCHANT_REGISTRATION", False):
            profile_choices.append((User.ProfileType.MERCHANT, _("تاجر - Merchant")))

        if getattr(config, "ENABLE_EDUCATIONAL_REGISTRATION", False):
            profile_choices.append(
                (User.ProfileType.EDUCATIONAL, _("تعليمي - Educational"))
            )

        self.fields["profile_type"].choices = profile_choices

    def clean_username(self):
        username = self.cleaned_data.get("username").lower()
        if User.objects.filter(username=username).exists():
            raise ValidationError(_("اسم المستخدم مستخدم من قبل. يرجى اختيار اسم آخر."))
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email").lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                _("هذا البريد الإلكتروني مسجل مسبقاً. يرجى استخدام بريد آخر.")
            )
        return email

    def clean_password(self):
        from django.contrib.auth.password_validation import validate_password

        password = self.cleaned_data.get("password")

        if password:
            try:
                # Validate password using Django's validators
                validate_password(password)
            except ValidationError as e:
                # Replace English error messages with Arabic
                arabic_errors = []
                for error in e.messages:
                    if "too short" in error.lower() or "at least" in error.lower():
                        arabic_errors.append(
                            _(
                                "كلمة المرور قصيرة جداً. يجب أن تحتوي على 8 أحرف على الأقل."
                            )
                        )
                    elif "too common" in error.lower() or "common" in error.lower():
                        arabic_errors.append(
                            _("كلمة المرور شائعة جداً. يرجى اختيار كلمة مرور أقوى.")
                        )
                    elif (
                        "numeric" in error.lower()
                        or "entirely numeric" in error.lower()
                    ):
                        arabic_errors.append(
                            _("كلمة المرور لا يمكن أن تكون أرقاماً فقط.")
                        )
                    elif "similar" in error.lower() or "personal" in error.lower():
                        arabic_errors.append(
                            _("كلمة المرور مشابهة جداً لبياناتك الشخصية.")
                        )
                    else:
                        arabic_errors.append(error)
                raise ValidationError(arabic_errors)

        return password

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise ValidationError(
                _("كلمتا المرور غير متطابقتين. يرجى التأكد من كتابتهما بشكل صحيح.")
            )
        return password2

    def clean_phone(self):
        from .utils import validate_phone_number, normalize_phone_number

        phone = self.cleaned_data.get("phone")
        country_code = self.data.get("country_code", "SA").upper()

        if not phone:
            raise ValidationError(_("رقم الجوال مطلوب"))

        # Validate format for the selected country
        if not validate_phone_number(phone, country_code):
            raise ValidationError(_("رقم الجوال غير صحيح لهذه الدولة"))

        # Normalize based on country
        normalized = normalize_phone_number(phone, country_code)

        # Check if already registered
        if User.objects.filter(phone=normalized).exists():
            raise ValidationError(_("رقم الجوال مسجل مسبقاً"))

        return normalized

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
