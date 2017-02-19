from django.forms import ModelForm, Form
from .models import originalImage
from django import forms


class UploadOriginalImageForm(ModelForm):
    class Meta:
        model = originalImage
        fields = ['userDescription', 'file']


class RegisterForm(Form):
    username = forms.CharField(max_length=100)
    email = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100)
