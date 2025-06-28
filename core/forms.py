from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, MissingPersonReport,ReportMessage

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

class ReportSearchForm(forms.Form):
    national_id = forms.CharField(required=False, label="National ID")
    image = forms.ImageField(required=False, label="Upload Face Image")
    age = forms.IntegerField(required=False)
    last_seen_location = forms.CharField(required=False) 
    name = forms.CharField(required=False, label="Name")

class ReportMessageForm(forms.ModelForm):
    class Meta:
        model = ReportMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your message...'}),
        }
