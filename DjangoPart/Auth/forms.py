from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "placeholder": "Введіть логін",
                "class": "w-full px-3 py-2 rounded bg-gray-800 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Введіть пароль",
                "class": "w-full px-3 py-2 rounded bg-gray-800 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            }
        )
    )
class CustomRegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Введіть логін",
                "class": "w-full px-3 py-2 rounded bg-gray-800 text-white border border-gray-600 "
                         "focus:outline-none focus:ring-2 focus:ring-blue-500"
            }
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Введіть пароль",
                "class": "w-full px-3 py-2 rounded bg-gray-800 text-white border border-gray-600 "
                         "focus:outline-none focus:ring-2 focus:ring-blue-500"
            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Підтвердіть пароль",
                "class": "w-full px-3 py-2 rounded bg-gray-800 text-white border border-gray-600 "
                         "focus:outline-none focus:ring-2 focus:ring-blue-500"
            }
        )
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()