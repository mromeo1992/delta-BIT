import httpx
import uuid
import shutil
import asyncio
import requests
from pathlib import Path
from nicegui import ui

DATASETS_DIR = Path("/data/datasets")
DATASETS_DIR.mkdir(parents=True, exist_ok=True)
STAGING_DIR = Path('/data/staging')
STAGING_DIR.mkdir(parents=True, exist_ok=True)

TOOLS_SERVER = "http://tools:8000"

async def handle_dataset_upload(e,dataset_name):
    file = e.file
    
    unique_name = f"{uuid.uuid4()}_{file.name}"
    staging_path = STAGING_DIR / unique_name

    temp_path = getattr(file, "_path", None)

    if temp_path and Path(temp_path).exists():
        shutil.copy(temp_path, staging_path)
    else:
        data = await file.read()
        staging_path.write_bytes(data)

    ui.notify(str(staging_path))
    try:
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(
                f"{TOOLS_SERVER}/upload_dataset",
                params={
                    "zip_path": str(staging_path),
                    "ds_name": dataset_name,
                },
            )
            response.raise_for_status()

        ui.notify("Dataset uploaded")

    except httpx.ReadTimeout:
        ui.notify("Upload timed out", color="negative")

    except httpx.HTTPError as e:
        ui.notify(f"HTTP error: {e}", color="negative")

def list_datasets():

    datasets = []

    if not DATASETS_DIR.exists():
        return datasets

    for folder in sorted(DATASETS_DIR.iterdir()):
    
        if not folder.is_dir():
            continue

        datasets.append(folder.name)

    return datasets

def get_dataset_images(dataset_name: str):
    dataset = DATASETS_DIR / dataset_name

    train = []
    test = []

    train_dir = dataset / "imagesTr"
    if train_dir.exists():
        train = sorted(train_dir.glob("*.nii*"))

    test_dir = dataset / "imagesTs"
    if test_dir.exists():
        test = sorted(test_dir.glob("*.nii*"))

    return train, test

def build_rows(files):
    rows = []

    for f in files:
        rows.append({
            "name": f.name,
            "label": f.stem,
            "size": f"{f.stat().st_size / 1024**2:.2f} MB"
        })

    return rows

async def handle_view_mri(e):
    row_name = e.args

    ui.notify(row_name)