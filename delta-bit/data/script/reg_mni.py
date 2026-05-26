from fastapi import FastAPI
import json
import os
import shutil
#config = json.load(open("/data/config/config.json"))
config_file = "/data/config/config.json"
job_file = "/data/config/job.json"
output_dir = "/data/NIFTI"
UPLOAD_DIR = "/data/uploads"
os.makedirs(output_dir, exist_ok=True)

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
        output_vim=os.path.join(os.path.dirname(im), "vim_prediction_native.nii.gz")
        ref= config["subjects"][sub]["images"][0]
        #output_vim = os.path.join(output_dir, "vim_prediction_native.nii.gz")
        matrix=os.path.join(os.path.dirname(im), "output0GenericAffine.mat")
        cmd="antsApplyTransforms -d 3 -i {} -r {} -o {} -t {} -n NearestNeighbor".format(im, ref, output_vim, str([matrix, 1]))
        print(f"Running command: {cmd}")
        os.system(cmd)

        update_config(sub,"native_predictions", output_vim)

    return {"status": "done"}