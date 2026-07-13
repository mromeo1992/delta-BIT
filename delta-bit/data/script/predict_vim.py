from .load_model import load_model
from .utils.utils import get_cropping_border
import json
import nibabel as nib
import numpy as np
import os
from skimage.measure import label
import requests


config_file='/data/script/utils/config_file.json' #gestisce i modelli e i parametri
config_data = '/data/config/config.json' #gestisce i path delle immagini
out_path = "/data/NIFTI/"

job_file = "/data/config/job.json"

border = get_cropping_border()
x_min , x_max = border['x_min'] , border['x_max']
y_min , y_max = border['y_min'] , border['y_max']
z_min , z_max = border['z_min'] , border['z_max']

#path=''

#img=nib.load(path)
#img_data=img.get_fdata()[x_min:x_max,y_min:y_max,z_min:z_max]
#print(config_data['model']['img_size'])

def update_config(sub , key, path_pred):
    config= json.load(open(config_data))
    if  key not in list(config["subjects"][sub].keys()):
        config["subjects"][sub][key] = []
    if path_pred not in config["subjects"][sub][key]:
        config["subjects"][sub][key].append(path_pred)
    with open(config_data, "w") as f:
        json.dump(config, f,indent=4)

def create_job_file_regMNI(path_file):
    job = {
        "command": "regMNI",
        "images": [path_file]
    }
    with open(job_file, "w") as f:
        json.dump(job, f, indent=4)

def create_job_file_revertMNI(path_file_in, path_file_out):
    job = {
        "command": "revertMNI",
        "images": [path_file_in ],
        "predictions": [path_file_out]
    }
    with open(job_file, "w") as f:
        json.dump(job, f, indent=4)

def create_job(sub, metadata, command):

    job = {"subjects": {sub: metadata}}
    job["command"] = command
    with open(job_file, "w") as f:
        json.dump(job, f, indent=4)              


def crop_image(img_data):
    return img_data[x_min:x_max,y_min:y_max,z_min:z_max]

def load_image(path):
    img = nib.load(path)
    img_data = img.get_fdata()
    #img_data = (img_data - np.min(img_data)) / (np.max(img_data) - np.min(img_data))
    affine = img.affine
    return img_data, affine

def predict_vim(config_img):

    def export_prediction(prediction, side):
        pred = prediction.squeeze()

        pred = (pred > 0.5).astype(np.uint8)
        labels, num=label(pred,return_num=1,connectivity=1)
        if num>1:
            j=np.zeros(num)
            for i in range(num):
                j[i]=len(np.where(labels==i+1)[0])
            biggest_component=np.where(j==np.max(j))[0]+1
            labels=labels==biggest_component
        pred=labels.astype('uint8')
        predi = np.zeros_like(img_data)
        predi[x_min:x_max, y_min:y_max, z_min:z_max] = pred
        out_path_img = os.path.join(patient_dir, "vim_prediction_left.nii.gz")

        if side == "right":
            predi = np.flip(predi, axis=0)  # Flip along the x-axis
            out_path_img = os.path.join(patient_dir, "vim_prediction_right.nii.gz")
        to_save = nib.Nifti1Image(predi, affine)
            
        nib.save(to_save, out_path_img)
        print(f"Saved prediction to {out_path_img}")
        update_config(sub, "predictions", out_path_img)
        config_img= json.load(open(config_data))
        pt_metadata = config_img['subjects'][sub]   
        create_job(sub, pt_metadata, command="revertMNI")
            #revert_transform
        try:
            response = requests.post("http://tools:8000/revert")
        except Exception as e:
            print(f"Request failed: {e}")


        if "dicom" in os.listdir(patient_dir):
            requests.post(
                        'http://tools:8000/convert_nifti_to_dicom', 
                        params={'sub_id': sub}
                    )            

        requests.post(
                'http://gui:8080/notify',
                json={'message': 'Subject {} completed'.format(sub)}
            )
        requests.post('http://gui:8080/refresh')        

    #config_data = json.load(open(config_img))
    #path_img = os.path.join(in_path, config_img['images'][0])
    config_model= json.load(open(config_file))
    model=load_model(config_model['model'])

    for sub in config_img['subjects'].keys():
        #path_img = im
        pt_metadata = config_img['subjects'][sub]
        side= pt_metadata['hemisphere_side'][0]
        patient_dir= os.path.join(out_path, sub)
        os.makedirs(patient_dir, exist_ok=True)
        reg_img=os.path.join(patient_dir, "T1_mni.nii.gz")
        if reg_img not in pt_metadata['registered']:
            print("Required registration, running registration pipeline...")
            create_job(sub, pt_metadata, command="regMNI")
            try:
                response = requests.post("http://tools:8000/run")
                config_img= json.load(open(config_data))
                pt_metadata = config_img['subjects'][sub]
            except Exception as e:
                print(f"Request failed: {e}")

        
        print(f"Loading image from {reg_img}")
        img_data, affine = load_image(reg_img)
        if side == "left":
            img_cropped = crop_image(img_data)
            img_cropped = img_cropped[np.newaxis, ..., np.newaxis]  # Aggiungi dimensioni batch e canali
            img_cropped = (img_cropped - np.min(img_cropped)) / (np.max(img_cropped) - np.min(img_cropped))
        elif side == "right":
            img_cropped = np.flip(img_data, axis=0)  # Flip along the x-axis
            img_cropped = crop_image(img_cropped)            
            img_cropped = img_cropped[np.newaxis, ..., np.newaxis]  # Aggiungi dimensioni batch e canali
            img_cropped = (img_cropped - np.min(img_cropped)) / (np.max(img_cropped) - np.min(img_cropped))
        elif side == "both":
            img_left = crop_image(img_data)
            img_left = img_left[np.newaxis, ..., np.newaxis]  # Aggi
            img_left = (img_left - np.min(img_left)) / (np.max(img_left) - np.min(img_left))
            img_right = np.flip(img_data, axis=0)  # Flip along the x-axis
            img_right = crop_image(img_right)
            img_right = img_right[np.newaxis, ..., np.newaxis]  # Aggiungi dimensioni batch e canali
            img_right = (img_right - np.min(img_right)) / (np.max(img_right) - np.min(img_right))
            img_cropped = np.concatenate((img_left, img_right), axis=0)  # Concatenate along the batch dimension
        
        prediction = model.predict(img_cropped)
        

        if side == "right" or side == "left":
            export_prediction(prediction, side)
        elif side == "both":
            export_prediction(prediction[0], "left")
            export_prediction(prediction[1], "right")        
            


    return {"status": "done"}

