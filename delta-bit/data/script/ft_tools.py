# ft_tools.py

import shutil
import zipfile
import requests
from pathlib import Path
from fastapi import FastAPI

UPLOAD_DIR = "/data/uploads"
DICOM_FOLDER = Path('DICOM')
STAGING_DIR = Path('/data/staging')

@app.post("/upload_database")
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