import os

from django import forms

from .models.story import Story, Reels


class StoriesForms(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['content']

    def clean_content(self):
        content = self.cleaned_data['content']
        file_extension = os.path.splitext(content.name)[1].lower()
        allowed_extensions = ['.png', '.jpg', '.jpeg', ".mp3", ".mp4", ".avi"]
        if file_extension not in allowed_extensions:
            raise forms.ValidationError("Content isn`t match correct type of object")
        return content


class ReelsForms(forms.ModelForm):
    class Meta:
        model = Reels
        fields = ['content', 'bio']

