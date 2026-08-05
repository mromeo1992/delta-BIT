import os
import numpy as np
import nibabel as nib
import pandas as pd
import datetime

import json

from tensorflow import keras
import keras.backend as K

from app.utils.paths import *
from app.utils.makedirs import make_pred_dirs
import app.src.data_loader as data_loader
import app.src.utils as utils

print("CLEARING SESSION")

K.clear_session()

###############
# LOAD CONFIG #
###############

print("LOADING CONFIG FILE")

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)
print(json.dumps(config, indent=2))

input_test_dir = config["paths"]["ftune_imagesTs"]
target_test_dir = config["paths"]["ftune_labelsTs"]

inference_model_path = config["paths"]["inference_model"]

img_size = tuple(config["model"]["img_size"])
num_input = config["model"]["num_input"]

########################
# SET PREDICTIONS INFO #
########################

# Set ID
pred_id=f"predictions_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
#import uuid
#pred_id = uuid.uuid4().hex[:6]

# Set/create predictions directory
dirs = make_pred_dirs(pred_id)

#############
# INFERENCE #
#############

# Load model
model=keras.models.load_model(inference_model_path, compile=False)

# Load data
test_gen=data_loader.data_test_loader(input_test_dir,target_test_dir,img_size,1,num_input)

predictions=model.predict(test_gen)
ind=len(target_test_dir)

# SONO QUI

to_save_folder=dirs["latest_pred_dir"]
#if to_save_folder not in os.listdir('./'):
#    os.mkdir('./'+to_save_folder)
#to_save_folder='./'+to_save_folder+'/'

for i in range(len(predictions[:,0,0,0,0])):
    img=predictions[i,:,:,:,:]
    img=img.reshape(img_size)
    img=np.array(img>0.5, 'uint8')
    affine=nib.load(test_gen.input_img_paths[i]).affine
    to_save=nib.Nifti1Image(img,affine)
    nib.save(to_save,to_save_folder+test_gen.target_img_paths[i][ind:])
print('done')

list_model=sorted(mdl for mdl in os.listdir(ckps_dir)
                  if mdl.endswith('.h5'))
model_2=os.path.join(ckps_dir,list_model[-1])

model_2=keras.models.load_model(model_2, compile=False)


#prediction test set
predictions=model_2.predict(test_gen)


#best prediction test set
to_save_folder='best_prediction_'+model_id
if to_save_folder not in os.listdir('./'):
    os.mkdir('./'+to_save_folder)
to_save_folder='./'+to_save_folder+'/'


for i in range(len(predictions[:,0,0,0,0])):
    img=predictions[i,:,:,:,:]
    affine=nib.load(test_gen.input_img_paths[i]).affine
    img=img.reshape(img_size)
    img=np.array(img>0.5,'uint8')
    to_save=nib.Nifti1Image(img,affine)
    nib.save(to_save,to_save_folder+test_gen.target_img_paths[i][ind:])
    print(to_save_folder+test_gen.target_img_paths[i][ind:])
print('best prediction done')