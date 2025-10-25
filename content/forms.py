from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    parent_id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Comment
        fields = ("body", "parent_id")
        widgets = {
            "body": forms.Textarea(
                attrs={"rows": 4, "placeholder": "اكتب تعليقك هنا..."}
            ),
        }
