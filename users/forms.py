from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Profile
from django.utils.safestring import mark_safe

User = get_user_model()

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Sign Up'))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# Update username and email
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    current_image = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control custom-readonly',
        }),
        label='Currently',
    )

    class Meta:
        model = Profile
        fields = ['image']

        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control custom-upload'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.image:
            try:
                public_id = self.instance.image.public_id
                self.fields['current_image'].initial = public_id
            except Exception as e:
                self.fields['current_image'].initial = "Unable to retrieve public_id"



