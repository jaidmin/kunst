from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Image(models.Model):
    file = models.ImageField()
    userDescription = models.CharField(max_length=140, null=True)
    pubDate = models.DateTimeField('pubDate' , null=True)


class originalImage(Image):
    def __unicode__(self):
        return "original_image_" + str(self.id)


class augmentedImage(Image):
    options = models.CharField(max_length=200)
    originalImage = models.ForeignKey(originalImage, on_delete=models.CASCADE,null=True)
    def __unicode__(self):
        return "augmented_image_" + str(self.id)