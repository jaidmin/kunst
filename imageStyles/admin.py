from django.contrib import admin
from models import originalImage, augmentedImage,generatingModelStyle, generatingModel, augmentedImageOptions
# Register your models here.
admin.site.register(originalImage)
admin.site.register(augmentedImage)

admin.site.register(generatingModel)
admin.site.register(generatingModelStyle)
admin.site.register(augmentedImageOptions)