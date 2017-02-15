from django.shortcuts import render
import uuid
import base64
from .forms import UploadOriginalImageForm
from io import  BytesIO
import PIL
from django.core.files.uploadedfile import InMemoryUploadedFile
import PIL.Image
from django.utils import timezone
from models import originalImage, augmentedImage
from tasks import generateAugmentedImage
from django.shortcuts import redirect
from django.http import HttpResponse

def index(request):
    return render(request,'index.html')


def images(request):
    originalImages = originalImage.objects.all()
    return render(request,'images.html',{'images': originalImages})


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
            processedFile = InMemoryUploadedFile(st, None, imagename, 'image/jpeg', len(st.getvalue()), None)
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
            return redirect('images')

    form = UploadOriginalImageForm()
    return render(request,'upload.html',{'form':form})


def exists(request):
    if request.method == 'POST':
        askedForImageId = request.augmentedImageId
        try:
            requestedAugmentedImage = augmentedImage.objects.get(id=askedForImageId)
        except augmentedImage.DoesNotExist:
            requestedAugmentedImage = None
        if(requestedAugmentedImage is not None):
            return HttpResponse(str(askedForImageId)+ " exists", status=200)
        else:
            return HttpResponse(str(askedForImageId)+ " does not exists", status=404)