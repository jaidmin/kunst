from django.shortcuts import render
import uuid
import base64
from .forms import UploadOriginalImageForm, RegisterForm, CreateAugmentedForm
from io import BytesIO
import PIL
from django.core.files.uploadedfile import InMemoryUploadedFile
import PIL.Image
from django.utils import timezone
from models import originalImage, augmentedImage, generatingModel, generatingModelStyle,augmentedImageOptions
from tasks import generateAugmentedImage
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse


def index(request):
    return render(request, 'index.html')


def images(request,scope):

    if scope == "private":
        originalImages = originalImage.objects.filter(owner = request.user)
        augmentedImages = augmentedImage.objects.filter(owner=request.user)
    else:
        originalImages = originalImage.objects.filter(public = True)
        augmentedImages = augmentedImage.objects.filter(public = True)

    renderCountAugmented = augmentedImages.count()
    renderCountOriginal = originalImages.count()
    return render(request, 'images.html', {'augmented_images': augmentedImages, 'renderCountAugmented': renderCountAugmented, 'renderCountOriginal': renderCountOriginal, 'scope': scope, 'original_images': originalImages})

def images_public(request):
    originalImages = originalImage.objects.filter(public= True)
    augmentedImages = augmentedImage.objects.filter(public= True)

    renderCount = augmentedImages.count()
    return render(request, 'images.html', {'images': augmentedImages, 'renderCount': renderCount,'scope': "public", 'original_images': originalImages})



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
            userDescription = form.cleaned_data['userDescription']
            if request.user.is_authenticated():
                owner = request.user
            else:
                owner = None
            public = form.cleaned_data['public']
            finalImage = originalImage(file=processedFile, userDescription=userDescription, pubDate=time,public=public,owner=owner)
            finalImage.save()

            # following section is to move to a celery task // legacy // is already in celery
            # demo that image can be encoded and decoded to a base64 string
            #  // use base64 rather than directly numpy array because of the size  (50* bigger)
            imageString = base64.b64encode(st.getvalue())

            # call to celery is to move to a seperate view, because image generation and uploading is being decoupled
            #generateAugmentedImage.delay(imageStringEncoded=imageString, userDescription=userDescription,
             #                            originalImageId=finalImage.id,public = finalImage.public)
            if owner is not None:
                return redirect('images_private')
            else:
                return redirect('images_public')

    form = UploadOriginalImageForm()
    return render(request, 'upload.html')
# think about how to make the thumbnails (half half style) -> numpy.tril gives me the lower traingle of a matrix, pil can
# merge with a filter applid to one image -> use one thumbnail make the filter all zeros in the upper
# triangle al 255 or 1 not sure, everywhere else, than merge. later a softer approach could be applied
#update thumbnails completely work very nicely the finished thumbnail is save in the aufmentedimage obejct since these are getting queried later


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

            return redirect("index")
        else:
            raise Exception(form)

    return render(request, template_name='registration/register.html')

def currentcount(request,scope,original_image_id=None):
    if scope == "public":
        currentCountAugmented = augmentedImage.objects.filter(public=True).count()
        currentCountOriginal =  originalImage.objects.filter(public=True).count()
        return JsonResponse({'currentCountAugmented': currentCountAugmented, 'currentCountOriginal': currentCountOriginal})
    if scope == "private":
        currentCountAugmented = augmentedImage.objects.filter(owner= request.user).count()
        currentCountOriginal =  originalImage.objects.filter(owner= request.user).count()
        return JsonResponse({'currentCountAugmented': currentCountAugmented, 'currentCountOriginal': currentCountOriginal})
    if scope == "single_image":
        currentCountAugmented = augmentedImage.objects.filter(originalImage.id == original_image_id).count()
        return JsonResponse({'currentCountAugmented': currentCountAugmented})
    return HttpResponse(status="404")




def image_detail(request,original_image_id):
    original_image = get_object_or_404(originalImage, id = original_image_id)

    if request.method == "POST":

        user = request.user
        if user.is_authenticated():
            if user == original_image.owner:
                form = CreateAugmentedForm(request.POST)

                if form.is_valid():
                    public = form.cleaned_data['public']
                    style_id = form.cleaned_data['style']
                    user_description = form.cleaned_data['user_description']

                    style = generatingModelStyle.objects.get(id=style_id)
                    st = BytesIO()
                    pil_image = PIL.Image.open(original_image.file)

                    pil_image.save(st, 'jpeg')
                    imageString = base64.b64encode(st.getvalue())

                    ### here comes the celery call --
                    # because the other object cannot be transferred



                    #note to self _ refactor substantial amounts, especially renaming

                    # also look at documentation of materialize and finish the form for generating a new augmenteImage
                    generateAugmentedImage.delay(imageStringEncoded=imageString, userDescription=user_description,
                                                 originalImageId=original_image.id, public=public,
                                                 model_id=style.model.id, style_number=style.number)
                    return redirect("image_detail", original_image_id)
                return HttpResponse(request.POST)
            return HttpResponse("youre not the owner")
        return  HttpResponse("youre note authenticated")



    augmented_images = augmentedImage.objects.filter(originalImage=original_image)
    #form = CreateAugmentedForm()
    styles = generatingModelStyle.objects.all()
    return render(request,template_name="image_detail.html",context={'original_image': original_image, 'augmented_images': augmented_images, 'styles': styles})








