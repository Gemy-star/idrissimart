# main/blog_forms.py
"""Forms for blog management"""

from django import forms
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.widgets import CKEditor5Widget
from content.models import Blog, BlogCategory


class BlogForm(forms.ModelForm):
    """Form for creating and editing blog posts"""

    class Meta:
        model = Blog
        fields = ["title", "content", "category", "image", "is_published"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("عنوان المدونة"),
                    "required": True,
                }
            ),
            "content": CKEditor5Widget(
                attrs={
                    "class": "form-control django_ckeditor_5",
                },
                config_name="extends",
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "image": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
            "is_published": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }
        labels = {
            "title": _("العنوان"),
            "content": _("المحتوى"),
            "category": _("الفئة"),
            "image": _("الصورة"),
            "is_published": _("نشر المدونة"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make category optional
        self.fields["category"].required = False
        self.fields["image"].required = False
