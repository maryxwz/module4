from django import forms

from backoffice.models import UserReport
from users.models import CustomUser

class UserSettingsForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ['is_private']
        widgets = {
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class UserReportForm(forms.ModelForm):

    class Meta:
        model = UserReport
        fields = ['description', 'content']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Детально опишіть, що саме порушує цей користувач...',
                'rows': 5,
                'required': True
            }),
            'content': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*,video/*,.pdf'
            }),
        }

    def clean_description(self):
        description = self.cleaned_data.get('description', '').strip()
        if len(description) < 10:
            raise forms.ValidationError('Опис скарги має містити принаймні 10 символів')
        return description