from .load_model import load_model
from .utils.utils import get_cropping_border

import json
import nibabel as nib
import numpy as np
import requests

border = get_cropping_border()
x_min , x_max = border['x_min'] , border['x_max']
y_min , y_max = border['y_min'] , border['y_max']
z_min , z_max = border['z_min'] , border['z_max']

def crop_image(img_data):
    return img_data[x_min:x_max,y_min:y_max,z_min:z_max]

def load_image(path):
    img = nib.load(path)
    img_data = img.get_fdata()
    img_data = (img_data - np.min(img_data)) / (np.max(img_data) - np.min(img_data))
    affine = img.affine
    return img_data, affine
