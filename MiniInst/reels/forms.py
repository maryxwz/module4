import os

from django import forms

from .models.reels import Reels

max_cont_size = MAX_CONTENT_LENGTH = 1024 * 1024 * 256

class ReelsForms(forms.ModelForm):
    class Meta:
        model = Reels
        fields = ['content', 'bio']

        widgets = {
            'content': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_content(self):
        content = self.cleaned_data['content']
        file_extension = os.path.splitext(content.name)[1].lower()
        content_size = content.size
        allowed_extensions = [".mp4", ".avi", ".ogg", ".MOV", ".wmv", ".flv", ".mkv", ".mpg", ".mpeg"]
        if file_extension not in allowed_extensions:
            raise forms.ValidationError("Тип вашого файлу не підходить під умови форми")
        if content_size > max_cont_size:
            raise forms.ValidationError("Ваше відео занадто великого розміру")
        return content


