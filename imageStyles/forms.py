from django.forms import ModelForm, Form
from .models import originalImage

class UploadOriginalImageForm(ModelForm):
    class Meta:
        model = originalImage
        fields = ['userDescription','file']

