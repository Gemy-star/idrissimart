from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import Comment
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
                config_name="admin",
                attrs={"class": "django_ckeditor_5"}
            ),
            "content_ar": CKEditor5Widget(
                config_name="admin",
                attrs={"class": "django_ckeditor_5"}
            ),
            "mission": CKEditor5Widget(
                config_name="admin",
                attrs={"class": "django_ckeditor_5"}
            ),
            "mission_ar": CKEditor5Widget(
                config_name="admin",
                attrs={"class": "django_ckeditor_5"}
            ),
            "vision": CKEditor5Widget(
                config_name="admin",
                attrs={"class": "django_ckeditor_5"}
            ),
            "vision_ar": CKEditor5Widget(
                config_name="admin",
                attrs={"class": "django_ckeditor_5"}
            ),
            "values": CKEditor5Widget(
                config_name="admin",
                attrs={"class": "django_ckeditor_5"}
            ),
            "values_ar": CKEditor5Widget(
                config_name="admin",
                attrs={"class": "django_ckeditor_5"}
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
