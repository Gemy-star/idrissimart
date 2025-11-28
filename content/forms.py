from django import forms

from .models import Comment


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
