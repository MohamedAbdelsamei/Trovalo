from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, MissingPersonReport

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class ReportForm(forms.ModelForm):
    class Meta:
        model = MissingPersonReport
        fields = ['name','national_id' ,'description', 'age', 'last_seen_location', 'image']

