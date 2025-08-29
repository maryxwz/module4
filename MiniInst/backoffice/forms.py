from django import forms
from users.models import CustomUser

class UserSettingsForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ['is_private']
        widgets = {
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
