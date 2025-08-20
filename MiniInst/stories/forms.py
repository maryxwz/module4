from django import forms

from .models.story import Story


class StoriesForms(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['content']
