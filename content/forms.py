from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import Comment


class CommentForm(forms.ModelForm):
    parent_id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Comment
        fields = ("body", "parent_id")
        widgets = {
            "body": CKEditor5Widget(config_name='default'),
        }
