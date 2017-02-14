from celery import shared_task
from django.utils import timezone
from PIL import Image
from io import BytesIO
import base64
from models import augmentedImage, originalImage
from django.core.files.uploadedfile import InMemoryUploadedFile


@shared_task
def generateAugmentedImage(imageString,originalImageId, userDescription,options="still have to find out how to deal with this"):
    imm_ = BytesIO(base64.b64decode(imageString))
    time = timezone.now()
    new_processed = InMemoryUploadedFile(imm_, None, "hallo.jpg", "image/jpeg", len(imm_.getvalue()), None)
    finalaugmented = augmentedImage(
        file=new_processed,
        userDescription=userDescription,
        pubDate=time,
        options="still have to think about that",
        originalImage= originalImage.objects.get(id = originalImageId)
    )
    finalaugmented.save()


