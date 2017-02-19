from __future__ import division
from __future__ import print_function
from celery import shared_task
from django.utils import timezone
from PIL import Image
from io import BytesIO
import base64
from models import augmentedImage, originalImage
from django.core.files.uploadedfile import InMemoryUploadedFile
import PIL.Image

import ast
import os

# internal imports

import numpy as np
import tensorflow as tf

from magenta.models.image_stylization import image_utils
from magenta.models.image_stylization import model
from magenta.models.image_stylization import ops
import uuid
from scipy.ndimage import convolve
import PIL.Image


# import the logging library
import logging

# Get an instance of a logger



@shared_task
def generateAugmentedImage(imageStringEncoded,originalImageId, userDescription):
    imageStringDecoded = BytesIO(base64.b64decode(imageStringEncoded))
    incomingImage = PIL.Image.open(imageStringDecoded)
    time = timezone.now()
    imageArray = np.expand_dims((np.array(incomingImage,dtype='float32') / 255),0)
    results = _multiple_images(imageArray,[3])
    imageName = str(uuid.uuid4()) + '.jpg'
    processedPILImage = results[1]
    processedImageBytes = BytesIO()
    processedPILImage.save(processedImageBytes,'jpeg')
    new_processed = InMemoryUploadedFile(processedImageBytes, None, imageName, "image/jpeg", len(processedImageBytes.getvalue()), None)

    original_image = incomingImage.resize(processedPILImage.size)
    thumbnail_new = create_thumbnail(original_image,processedPILImage)

    thumbnail_name = str(uuid.uuid4()) + '.jpg'
    thumbnail_bytes = BytesIO()
    thumbnail_new.save(thumbnail_bytes,'jpeg')
    thumbnail_processed = InMemoryUploadedFile(thumbnail_bytes,None,thumbnail_name,"image/jpeg",len(thumbnail_bytes.getvalue()), None)

    finalaugmented = augmentedImage(
        file=new_processed,
        userDescription=userDescription,
        pubDate=time,
        options="still have to think about that",
        originalImage= originalImage.objects.get(id=originalImageId),
        thumbnail = thumbnail_processed
    )
    finalaugmented.save()



def _load_checkpoint(sess, checkpoint):
  """Loads a checkpoint file into the session."""
  model_saver = tf.train.Saver(tf.global_variables())
  checkpoint = os.path.expanduser(checkpoint)
  if tf.gfile.IsDirectory(checkpoint):
    checkpoint = tf.train.latest_checkpoint(checkpoint)
    tf.logging.info('loading latest checkpoint file: {}'.format(checkpoint))
  model_saver.restore(sess, checkpoint)


def _multiple_images(input_image, which_styles):
  """Stylizes an image into a set of styles and returns array of tuples with style as first and PIL image as second element"""
  with tf.Graph().as_default(), tf.Session() as sess:
    stylized_images = model.transform(
        input_image,
        normalizer_params={
            'labels': tf.constant(which_styles),
            'num_categories': 10, # monet has 10 categories varied has 34
            'center': True,
            'scale': True})
    _load_checkpoint(sess, '/home/jaidmin/PycharmProjects/kunst/imageStyles/tensorflow_models/monet.ckpt')

    stylized_image = stylized_images.eval()
    results = []
    one_image = PIL.Image.fromarray((stylized_image[0] * 255).astype('uint8'))
    return (which_styles,one_image)



mask_skeleton =np.rot90(np.triu(np.ones((1000,1000))*255).astype('float32'))
maskimage_skeleton = PIL.Image.fromarray(mask_skeleton.astype('uint8'),mode='L')
average_convolution = np.ones((50,50))/2500


def create_thumbnail(original_image, augmented_image,maskimage_skeleton = maskimage_skeleton,convolution = average_convolution):
    thumbnail = original_image.copy()
    maskimage_skeleton = maskimage_skeleton.resize(original_image.size)
    mask = np.array(maskimage_skeleton)
    mask = convolve(mask, convolution)
    mask = mask.astype('uint8')
    maskimage = PIL.Image.fromarray(mask, mode='L')
    thumbnail.paste(augmented_image,mask = maskimage )
    return thumbnail

