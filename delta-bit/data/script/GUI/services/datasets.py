import httpx
import uuid
import shutil
import asyncio
from pathlib import Path

DATASETS_DIR = Path("/data/datasets")
DATASETS_DIR.mkdir(parents=True, exist_ok=True)
STAGING_DIR = Path('/data/staging')
STAGING_DIR.mkdir(parents=True, exist_ok=True)

TOOLS_SERVER = "http://tools:8000"

async def handle_dataset_upload(e):
    file = e.file

    unique_name = f"{uuid.uuid4()}_{file.name}"
    staging_path = STAGING_DIR / unique_name

    temp_path = getattr(file, "_path", None)

    if temp_path and Path(temp_path).exists():
        shutil.copy(temp_path, staging_path)
    else:
        data = await file.read()
        staging_path.write_bytes(data)

    async with httpx.AsyncClient() as client:
        await client.post(
            f'{TOOLS_SERVER}/upload_dataset',
            params={'zip_path': str(staging_path)}
        )

def list_datasets():

    datasets = []

    if not DATASETS_DIR.exists():
        return datasets

    for folder in sorted(DATASETS_DIR.iterdir()):
    
        if not folder.is_dir():
            continue

        datasets.append(folder.name)

    return datasets

def remove_dataset():
    pass