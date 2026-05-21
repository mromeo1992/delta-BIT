from .load_model import load_model
from .utils.utils import get_cropping_border
import json
import nibabel as nib
import numpy as np
import os

config='data/script/utils/config_file.json'
config_data = json.load(open(config))
out_path = "data/NIFTI/"
in_path = "/app"

border = get_cropping_border()
x_min , x_max = border['x_min'] , border['x_max']
y_min , y_max = border['y_min'] , border['y_max']
z_min , z_max = border['z_min'] , border['z_max']

#path=''

#img=nib.load(path)
#img_data=img.get_fdata()[x_min:x_max,y_min:y_max,z_min:z_max]
#print(config_data['model']['img_size'])

def crop_image(img_data):
    return img_data[x_min:x_max,y_min:y_max,z_min:z_max]

def load_image(path):
    img = nib.load(path)
    img_data = img.get_fdata()
    affine = img.affine
    return img_data, affine

def predict_vim(config_img):
    #path_img = os.path.join(in_path, config_img['images'][0])
    path_img = os.path.join(in_path, config_img['predictions'][0][1:])
    out_path_img = os.path.join(out_path, "vim_prediction.nii.gz")
    print(f"Loading image from {path_img}")
    img_data, affine = load_image(path_img)
    img_cropped = crop_image(img_data)
    img_cropped = img_cropped[np.newaxis, ..., np.newaxis]  # Aggiungi dimensioni batch e canali
    model=load_model(config_data['model'])
    prediction = model.predict(img_cropped)
    prediction = prediction.squeeze()
    pred = np.zeros_like(img_data)
    pred[x_min:x_max, y_min:y_max, z_min:z_max] = prediction
    to_save = nib.Nifti1Image(pred, affine)
    nib.save(to_save, out_path_img)

