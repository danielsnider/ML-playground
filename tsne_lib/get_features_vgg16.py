#!/usr/bin/python
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # disables warning: Your CPU supports instructions that this TensorFlow binary was not compiled to use: SSE4.1 SSE4.2 AVX AVX2 FMA

import time
from tsne_lib import utils 
import csv
import pandas as pd
import glob
import skimage
import skimage.io
import scipy
import numpy as np
import mahotas as mh
import tensorflow as tf
import tensorflow.contrib.slim.nets as nets

from PIL import Image
from IPython import embed
from tensorflow.python.tools import inspect_checkpoint as chkp
from sklearn.metrics import average_precision_score
from skimage.transform import rescale, resize


slim = tf.contrib.slim
vgg = nets.vgg

def vgg16(filenames, session_id, res,perplexity, early_exaggeration, learning_rate, dpi):
  # Load images
  images = np.zeros((len(filenames), 224, 224, 3), dtype=np.float32)
  for i, imageName in enumerate(filenames): 
    print(i, imageName)
    img = skimage.io.imread(imageName)
    if len(img.shape) == 2:
      # we have a 2D, black and white image but  vgg16 needs 3 channels
      img = np.expand_dims(img,2)
      img = np.repeat(img, 3, axis=2)
    #img = scipy.misc.imresize(img, (224,224))
    img =  resize(img, (224, 224), anti_aliasing=True)
    images[i,:,:,:] = img

  in_images = tf.placeholder(tf.float32, images.shape)

  with slim.arg_scope(vgg.vgg_arg_scope()):
    model, intermed = vgg.vgg_16(in_images, is_training=False)
    fc7 = intermed['vgg_16/fc7']
    restored_variables = tf.contrib.framework.get_variables_to_restore()
    restorer = tf.train.Saver(restored_variables)
    with tf.Session() as sess:
      img_net_path = 'models/vgg_16.ckpt'
      restorer.restore(sess, img_net_path)
      features = sess.run(fc7, feed_dict={in_images:images})
  # Clean up model
  tf.reset_default_graph()
  features = features.squeeze()
  utils.save_features_to_csv_file(features, filenames, session_id, 'VGG16_features:Resolution:%d_Perplexity:%d_EarlyExaggeration:%d_LearningRate:%d_DPI:%d.csv' % (res,perplexity, early_exaggeration, learning_rate, dpi))
  return features 

