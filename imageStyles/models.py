from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Image(models.Model):
    owner = models.ForeignKey(User,null=True)
    file = models.ImageField()
    #bewertung = models.CharField()
    userDescription = models.CharField(max_length=140, null=True)
    pubDate = models.DateTimeField('pubDate' , null=True)
    public = models.BooleanField(default=False)


class originalImage(Image):
    def __unicode__(self):
        return "original_image_" + str(self.id)


class augmentedImage(Image):
    options = models.CharField(max_length=200)
    originalImage = models.ForeignKey(originalImage, on_delete=models.CASCADE,null=True)
    def __unicode__(self):
        return "augmented_image_" + str(self.id)