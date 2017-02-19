from django.shortcuts import render
import uuid
import base64
from .forms import UploadOriginalImageForm, RegisterForm
from io import BytesIO
import PIL
from django.core.files.uploadedfile import InMemoryUploadedFile
import PIL.Image
from django.utils import timezone
from models import originalImage, augmentedImage
from tasks import generateAugmentedImage
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse


def index(request):
    return render(request, 'index.html')


def images(request):
    # originalImages = originalImage.objects.all()
    augmentedImages = augmentedImage.objects.all()
    renderCount = augmentedImages.count()
    return render(request, 'images.html', {'images': augmentedImages, 'renderCount': renderCount})


def upload(request):
    if request.method == 'POST':
        form = UploadOriginalImageForm(request.POST, request.FILES)
        # check if form is valid
        if form.is_valid():
            uploadedFile = form.cleaned_data['file']

            # resize image
            basewidth = 500
            imagename = str(uuid.uuid4()) + '.jpg'
            img = PIL.Image.open(uploadedFile)
            wpercent = (basewidth / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            st = BytesIO()
            img.resize((basewidth, hsize), PIL.Image.ANTIALIAS).save(st, 'jpeg')

            # add image to db
            processedFile = InMemoryUploadedFile(st, None, imagename, 'image/jpeg', len(st.getvalue()), None)
            time = timezone.now()
            userDescription = "test"
            userDescription = form.cleaned_data['userDescription']
            finalImage = originalImage(file=processedFile, userDescription=userDescription, pubDate=time)
            finalImage.save()

            # following section is to move to a celery task // legacy // is already in celery
            # demo that image can be encoded and decoded to a base64 string
            #  // use base64 rather than directly numpy array because of the size  (50* bigger)
            imageString = base64.b64encode(st.getvalue())

            # call to celery
            generateAugmentedImage.delay(imageStringEncoded=imageString, userDescription=userDescription,
                                         originalImageId=finalImage.id)
            return redirect('images')

    form = UploadOriginalImageForm()
    return render(request, 'upload.html', {'form': form})
# think about how to make the thumbnails (half half style) -> numpy.tril gives me the lower traingle of a matrix, pil can
#merge with a filter applid to one image -> use one thumbnail make the filter all zeros in the upper triangle al 255 or 1 not sure, everywhere else, than merge. later a softer approach could be applied 

def register(request):
    form = RegisterForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            data = form.cleaned_data
            username = data['username']
            email = data['email']
            password = data['password']
            user = User.objects.create_user(username, email, password)
            user.save()

            redirect('')
        else:
            raise Exception(form)

    return render(request, template_name='registration/register.html')

def currentcount(request):
    currentCount = augmentedImage.objects.all().count()
    return JsonResponse({'currentCount':currentCount})
