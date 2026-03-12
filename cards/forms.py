from __future__ import annotations

from django import forms

from .models import KnowledgeCard


class KnowledgeCardForm(forms.ModelForm):
    images = forms.ImageField(
        required=True,
        widget=forms.ClearableFileInput(attrs={"accept": "image/*"}),
        help_text="Upload one primary image",
    )

    class Meta:
        model = KnowledgeCard
        fields = ["title", "summary", "description", "tags"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Persian Cat"}),
            "summary": forms.Textarea(attrs={"rows": 3, "placeholder": "Short summary for result cards"}),
            "description": forms.Textarea(attrs={"rows": 6, "placeholder": "Full description"}),
            "tags": forms.TextInput(attrs={"placeholder": "cat, pet, fluffy"}),
        }


class KeywordSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by title, tags, description, or image"}),
    )
    sort = forms.ChoiceField(
        required=False,
        choices=[("recent", "Most Recent"), ("title", "Title"), ("oldest", "Oldest")],
    )


class ImageSearchForm(forms.Form):
    query_image = forms.ImageField(required=True, widget=forms.ClearableFileInput(attrs={"accept": "image/*"}))


class KnowledgeCardUpdateForm(forms.ModelForm):
    class Meta:
        model = KnowledgeCard
        fields = ["title", "summary", "description", "tags"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Persian Cat"}),
            "summary": forms.Textarea(attrs={"rows": 3}),
            "description": forms.Textarea(attrs={"rows": 6}),
            "tags": forms.TextInput(attrs={"placeholder": "cat, pet, fluffy"}),
        }


class CardImageUploadForm(forms.Form):
    images = forms.ImageField(
        required=True,
        widget=forms.ClearableFileInput(attrs={"accept": "image/*"}),
        help_text="Select one image to replace current primary image",
    )
