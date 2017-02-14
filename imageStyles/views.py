from django.shortcuts import render
from django.http import HttpResponse
import uuid
import base64
# Create your views here.
from .forms import UploadOriginalImageForm
from io import StringIO, BytesIO
import PIL
from django.core.files.uploadedfile import InMemoryUploadedFile
import PIL.Image
from django.utils import timezone
from models import originalImage, augmentedImage
from tasks import generateAugmentedImage
from PIL import Image

def index(request):
    return render(request,'index.html')


def images(request):
    return render(request,'images.html')


def upload(request):
    if request.method =='POST':
        form = UploadOriginalImageForm(request.POST, request.FILES)
        # check if form is valid
        if form.is_valid():
            uploadedFile = form.cleaned_data['file']
            basewidth = 500
            imagename = str(uuid.uuid4())+ '.jpg'
            img = PIL.Image.open(uploadedFile)
            wpercent = (basewidth / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            st = BytesIO()
            img.resize((basewidth, hsize), PIL.Image.ANTIALIAS).save(st, 'jpeg')

            processedFile = InMemoryUploadedFile(st, None, imagename, 'image/jpeg',
                                                  len(st.getvalue()), None)
            time = timezone.now()
            userDescription = "test"
            userDescription = form.cleaned_data['userDescription']
            finalImage = originalImage(file=processedFile, userDescription=userDescription,pubDate=time)
            finalImage.save()


            # following section is to move to a celery task
            # demo that image can be encoded and decoded to a base64 string
            imageString = base64.b64encode(st.getvalue())

            #call to celery
            generateAugmentedImage.delay(imageString,userDescription=userDescription,originalImageId=finalImage.id)


            '''imm_ = BytesIO(base64.b64decode(imageString))
            new_processed = InMemoryUploadedFile(imm_, None, "hallo.jpg", "image/jpeg", len(imm_.getvalue()), None)
            finalaugmented = augmentedImage(
                file=new_processed,
                userDescription=userDescription,
                pubDate=time,
                options="still have to think about that",
                originalImage= originalImage.objects.get(id = finalImage.id))
            finalaugmented.save()
'''


            return render(request,'images.html')

    form = UploadOriginalImageForm()
    return render(request,'upload.html',{'form':form})



