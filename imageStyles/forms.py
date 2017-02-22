from django.forms import ModelForm, Form
from .models import originalImage, generatingModelStyle
from django import forms


class UploadOriginalImageForm(ModelForm):
    class Meta:
        model = originalImage
        fields = ['userDescription', 'file','public']


class RegisterForm(Form):
    username = forms.CharField(max_length=100)
    email = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100)


class CreateAugmentedForm(Form):
    public = forms.BooleanField()
    style = forms.ChoiceField(choices=[(style.id,style.name) for style in generatingModelStyle.objects.all()])
    user_description = forms.CharField(max_length=140)