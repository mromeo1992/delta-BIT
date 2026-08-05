import httpx
import uuid
import shutil
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
            #response.raise_for_status()

        #ui.notify("Dataset uploaded")

    except httpx.ReadTimeout:
        ui.notify("Upload timed out", color="negative")

    except httpx.HTTPError as e:
        ui.notify(f"HTTP error: {e}", color="negative")

    return response.json()

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

def build_rows(files, dataset_name):
    rows = []

    for f in files:
        rows.append({
            "dataset": dataset_name,
            "name": f.name,
            "label": f.stem,
            "size": f"{f.stat().st_size / 1024**2:.2f} MB"
        })

    return rows

TRAIN_TABLE_SLOT = r'''
    <q-tr :props="props" class="cursor-pointer">

        <q-td key="name" :props="props" class="text-left">
            {{ props.row.name }}
        </q-td>

        <q-td key="label" :props="props" class="text-left">
            {{ props.row.label }}
        </q-td>

        <q-td key="size" :props="props" class="text-left">
            {{ props.row.size }}
        </q-td>

        <q-td key="view" class="text-left" @click.stop>
            <q-btn
                size="sm"
                color="secondary"
                icon="visibility"
                round
                dense
                @click="() => $parent.$parent.$emit('view_mri', 
                    {
                    'dataset': props.row.dataset,
                    'table': 'train',
                    'file' : props.row.name
                    }
                    )"
            />
        </q-td>

    </q-tr>
'''

TEST_TABLE_SLOT = r'''
    <q-tr :props="props" class="cursor-pointer">

        <q-td key="name" :props="props" class="text-left">
            {{ props.row.name }}
        </q-td>

        <q-td key="label" :props="props" class="text-left">
            {{ props.row.label }}
        </q-td>

        <q-td key="size" :props="props" class="text-left">
            {{ props.row.size }}
        </q-td>

        <q-td key="view" class="text-left" @click.stop>
            <q-btn
                size="sm"
                color="secondary"
                icon="visibility"
                round
                dense
                @click="() => $parent.$parent.$emit('view_mri', 
                    {
                    'dataset': props.row.dataset,
                    'table': 'test',
                    'file' : props.row.name
                    }
                    )"
            />
        </q-td>

    </q-tr>
'''

DATASET_REQUIREMENTS =r"""
    **Dataset requirements**

    - Scans and labels must be in **NIfTI** format (`.nii` or `.nii.gz`).
    - All images must be registered to the **MNI 1 mm standard space**.
    - The dataset must contain **at least 10 samples** in the training (one sample only for 10% validation split).<br>
            *Suggested minimum: 50 samples for training.*
    - The dataset must have the following structure:

    ```
    dataset_name/
    ├── imagesTr/
    │   ├── image1.nii.gz
    │   ├── image2.nii.gz
    │   └── ...
    ├── labelsTr/
    │   ├── label1.nii.gz
    │   ├── label2.nii.gz
    │   └── ...
    ├── imagesTs/ *[optional] for model validation*
    │   ├── image1.nii.gz
    │   ├── image2.nii.gz
    │   └── ...
    └── labelsTs/ *[optional] for model validation*
        ├── label1.nii.gz
        ├── label2.nii.gz
        └── ...
    ```
"""