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


@shared_task
def generateAugmentedImage(imageStringEncoded,originalImageId, userDescription):
    imageStringDecoded = BytesIO(base64.b64decode(imageStringEncoded))
    incomingImage = PIL.Image.open(imageStringDecoded)
    time = timezone.now()
    imageArray = np.expand_dims((np.array(incomingImage,dtype='float32') / 255),0)
    results = _multiple_images(imageArray,[3])
    imageName = str(uuid.uuid4()) + '.jpg'
    processedPILImage = results[0][1]
    processedImageBytes = BytesIO()
    processedPILImage.save(processedImageBytes,'jpeg')
    new_processed = InMemoryUploadedFile(processedImageBytes, None, imageName, "image/jpeg", len(processedImageBytes.getvalue()), None)
    finalaugmented = augmentedImage(
        file=new_processed,
        userDescription=userDescription,
        pubDate=time,
        options="still have to think about that",
        originalImage= originalImage.objects.get(id = originalImageId)
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
        tf.concat_v2([input_image for _ in range(len(which_styles))], 0),
        normalizer_params={
            'labels': tf.constant(which_styles),
            'num_categories': 10, # monet has 10 categories varied has 34
            'center': True,
            'scale': True})
    _load_checkpoint(sess, '/home/jaidmin/PycharmProjects/kunst/imageStyles/tensorflow_models/monet.ckpt')

    stylized_images = stylized_images.eval()
    results = []
    for which, stylized_image in zip(which_styles, stylized_images):
        one_image = PIL.Image.fromarray((stylized_images[0] * 255).astype('uint8'))
        results.append((which,one_image))
    return results