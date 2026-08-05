from .load_model import load_model
from .utils.utils import get_cropping_border

from tensorflow import keras
import keras.backend as K

import json
import nibabel as nib
import numpy as np
import requests
from pathlib import Path

FT_FOLDER = Path("/data/fine_tuning")
MODELS_DIR = Path("/data/MODELS")
DATASETS_DIR = Path("/data/datasets")

def crop_image(img_data):

    border = get_cropping_border()
    x_min , x_max = border['x_min'] , border['x_max']
    y_min , y_max = border['y_min'] , border['y_max']
    z_min , z_max = border['z_min'] , border['z_max']
    
    return img_data[x_min:x_max,y_min:y_max,z_min:z_max]

def load_image(path):
    img = nib.load(path)
    img_data = img.get_fdata()
    img_data = (img_data - np.min(img_data)) / (np.max(img_data) - np.min(img_data))
    affine = img.affine
    return img_data, affine

def finetuning():
    print("CLEARING SESSION")

    K.clear_session()

    ###############
    # LOAD CONFIG #
    ###############

    print("LOADING CONFIG FILE")

    with open(FT_FOLDER / "config.json", "r") as f:
        config = json.load(f)

    ################
    # SET UP MODEL #
    ################

    model_config = config['model']
    model = load_model(model_config)
