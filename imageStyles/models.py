from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Image(models.Model):
    owner = models.ForeignKey(User, null=True)
    file = models.ImageField()
    userDescription = models.CharField(max_length=140, null=True)
    pubDate = models.DateTimeField('pubDate', null=True)
    public = models.BooleanField(default=False)


class originalImage(Image):
    def __unicode__(self):
        return "original_image_" + str(self.id)





class generatingModel(models.Model):
    name = models.CharField(max_length=140)
    model_path = models.CharField(max_length=300)

    def __unicode__(self):
        return self.name

class generatingModelStyle(models.Model):
    model = models.ForeignKey(generatingModel)
    name = models.CharField(max_length=140)
    number = models.IntegerField()
    description = models.CharField(max_length=140)
    image = models.ImageField()

    def __unicode__(self):
        return self.model.name + "_" + str(self.number)





class augmentedImageOptions(models.Model):
    model = models.ForeignKey(generatingModel)
    style = models.ForeignKey(generatingModelStyle)

    def __unicode__(self):
        return self.model.name + "_" + str(self.style.number) + "_" + str(self.id)


class augmentedImage(Image):
    options = models.ForeignKey(augmentedImageOptions)
    originalImage = models.ForeignKey(originalImage, on_delete=models.CASCADE, null=True)
    thumbnail = models.ImageField()

    def __unicode__(self):
        return "augmented_image_" + str(self.id)



