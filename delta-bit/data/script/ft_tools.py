# ft_tools.py
import shutil
import zipfile
import requests
from pathlib import Path

UPLOAD_DIR = "/data/uploads"
DATASETS_DIR = Path('/data/datasets')
STAGING_DIR = Path('/data/staging')



def extract_dataset(zip_path : str, ds_name : str):
    ds_folder=DATASETS_DIR / ds_name
    ds_folder.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(ds_folder)
    
    requests.post(
                'http://gui:8080/notify',
                json={'message': 'Dataset uploaded'}
            )
    #requests.post('http://gui:8080/refresh')
    shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    return {"status": "done"}