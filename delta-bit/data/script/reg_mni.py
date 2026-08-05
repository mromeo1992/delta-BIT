from fastapi import FastAPI
import json
import os
import shutil
import zipfile
import pydicom
import pathlib
import requests
import subprocess

from script.ft_tools import extract_dataset


#config = json.load(open("/data/config/config.json"))
config_file = "/data/config/config.json"
job_file = "/data/config/job.json"
output_dir = pathlib.Path("/data/NIFTI")
UPLOAD_DIR = "/data/uploads"
DICOM_FOLDER = pathlib.Path('DICOM')
STAGING_DIR = pathlib.Path('/data/staging')
output_dir.mkdir(parents=True, exist_ok=True)
DICOM_FOLDER.mkdir(parents=True, exist_ok=True)


def update_config(sub , key, path_pred):
    config= json.load(open(config_file))
    if  key not in list(config["subjects"][sub].keys()):
        config["subjects"][sub][key] = []
    if path_pred not in config["subjects"][sub][key]:
        config["subjects"][sub][key].append(path_pred)
    with open(config_file, "w") as f:
        json.dump(config, f,indent=4)

app = FastAPI()

@app.post("/run")
def run_registration():
    # qui parte la tua pipeline
    #read config
    # esegui ants
    config= json.load(open(job_file))
    mni="/data/script/utils/MNI152_T1_1mm.nii.gz"
    sub = list(config["subjects"].keys())[0]
    img=config["subjects"][sub]["images"]
    print(f"Subject: {sub}, Images: {img}")
    for i in img:
        print(f"Processing {i} with MNI template {mni}")
        cmd=f"antsRegistrationSyNQuick.sh -d 3 -f {mni} -m {i} -t r"
        out_path="outputWarped.nii.gz"
        print(f"Running command: {cmd}")
        os.system(cmd)
        out_dir=os.path.join(output_dir,sub)
        os.makedirs(out_dir, exist_ok=True)
        out_img=os.path.join(out_dir, "T1_mni.nii.gz")
        #shutil.copy(out_path, os.path.join(output_dir, "T1_mni.nii.gz"))
        update_config(sub, "registered", out_img)
        #print(config)
        print("Cleaning up temporary files...")
        for f in os.listdir("/data"):
            if f.startswith("output"):
                #os.remove(os.path.join("/data", f))
                shutil.move(os.path.join("/data", f), os.path.join(out_dir, f))
                if f==out_path:
                    shutil.move(os.path.join(out_dir, f), os.path.join(out_dir, "T1_mni.nii.gz"))
        

    return {"status": "done"}

@app.post("/revert")
def revert_registration():
    config = json.load(open(job_file))
    sub = list(config["subjects"].keys())[0]
    for im in config["subjects"][sub]["predictions"]:
        print(im)
        output_vim=im.replace("vim_prediction", "vim_prediction_native")#os.path.join(os.path.dirname(im), "vim_prediction_native.nii.gz")
        ref= config["subjects"][sub]["images"][0]
        #output_vim = os.path.join(output_dir, "vim_prediction_native.nii.gz")
        matrix=os.path.join(os.path.dirname(im), "output0GenericAffine.mat")
        cmd="antsApplyTransforms -d 3 -i {} -r {} -o {} -t {} -n NearestNeighbor".format(im, ref, output_vim, str([matrix, 1]))
        print(f"Running command: {cmd}")
        os.system(cmd)

        update_config(sub,"native_predictions", output_vim)

    return {"status": "done"}

def convert_dicom_to_nifti():
    for f in os.listdir(DICOM_FOLDER):
        dicom_path = DICOM_FOLDER / f

        if not dicom_path.is_dir():
            continue

        dcm_files = [x for x in os.listdir(dicom_path) if x.endswith(".dcm")]
        if not dcm_files:
            continue

        dicom_file = dicom_path / dcm_files[0]
        meta = pydicom.dcmread(dicom_file)

        patient_id = meta.PatientID
        i = 0
        existing = set(os.listdir(output_dir))

        while patient_id in existing:
            i += 1
            patient_id = f"{meta.PatientID}_{i}"

        patient_folder = output_dir / patient_id
        patient_folder.mkdir(exist_ok=True)

        cmd = [
            "dcm2niix", "-v", "y", "-z", "y",
            "-f", "nativeT1",
            "-o", str(patient_folder),
            str(dicom_path)
        ]

        subprocess.run(cmd, check=True)

        shutil.move(dicom_path, patient_folder / "dicom")
            #requests.post(
            #    'http://gui:8080/notify',
            #    json={'message': 'Subject {} created'.format(patient_id)}
            #)
            #requests.post('http://gui:8080/refresh')
    #shutil.rmtree(DICOM_FOLDER)
    #DICOM_FOLDER.mkdir(exist_ok=True)        

    return {"status": "done"}


@app.post("/upload_dcm")
def extract_zip(zip_path : str):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(DICOM_FOLDER)
    convert_dicom_to_nifti()
    requests.post(
                'http://gui:8080/notify',
                json={'message': 'All subjects created'}
            )
    requests.post('http://gui:8080/refresh')
    shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    return {"status": "done"}

@app.post("/convert_nifti_to_dicom")
def convert_nifti_to_dicom(sub_id):
    dicom_folder = output_dir / sub_id / 'dicom'
    nifti_file = [output_dir/sub_id / f for f in os.listdir(output_dir / sub_id) if f.startswith('vim_prediction_native') and f.endswith('.nii.gz')]
    
    for f in nifti_file:
        if "left" in f.name:
            side = "left"
            patient_folder = output_dir / sub_id / 'vim_seg_left.dcm'
        
        elif "right" in f.name:
            side = "right"
            patient_folder = output_dir / sub_id / 'vim_seg_right.dcm'
        metadata_json = "/data/script/utils/metadata_" + side + ".json"            

        

        cmd = "itkimage2segimage --verbose --inputImageList {} --inputDICOMDirectory {} --outputDICOM {} --inputMetadata {}".format(
            f,
            dicom_folder,
            patient_folder,
            metadata_json
        )
        os.system(cmd)
        requests.post(
                    'http://gui:8080/notify',
                    json={'message': 'Subject {} DICOM created'.format(sub_id)}
                )
    return {"status": "done"}



#Parte fine tuning
@app.post("/upload_dataset")
def upload_dataset(zip_path : str, ds_name : str):
    
    status = extract_dataset(zip_path, ds_name)

    if status['status'] == 'failed':
        requests.post(
            'http://gui:8080/notify',
            json={'message': f'Failed to extract dataset {ds_name}', 'type': 'negative'}
        )
      
    return status