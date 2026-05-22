from fastapi import FastAPI
import json
import os
import shutil
config = json.load(open("/data/config/config.json"))
output_dir = "/data/NIFTI"
UPLOAD_DIR = "/data/uploads"
os.makedirs(output_dir, exist_ok=True)

def update_config(path_pred):
    config['predictions'] = [path_pred]
    with open("/data/config/config.json", "w") as f:
        json.dump(config, f)

app = FastAPI()

@app.post("/run")
def run_registration():
    # qui parte la tua pipeline
    #read config
    # esegui ants
    mni="/data/script/utils/MNI152_T1_1mm.nii.gz"
    img=config["images"]
    for i in img:
        im=os.path.join(UPLOAD_DIR,i)
        print(f"Processing {im} with MNI template {mni}")
        cmd=f"antsRegistrationSyNQuick.sh -d 3 -f {mni} -m {im} -t a"
        out_path="outputWarped.nii.gz"
        print(f"Running command: {cmd}")
        os.system(cmd)
        
        shutil.copy(out_path, os.path.join(output_dir, "T1_mni.nii.gz"))
        update_config(os.path.join(output_dir, "T1_mni.nii.gz"))
        print(config)
        print("Cleaning up temporary files...")
        for f in os.listdir("/data"):
            if f.startswith("output"):
                os.remove(os.path.join("/data", f))
        

    return {"status": "done"}