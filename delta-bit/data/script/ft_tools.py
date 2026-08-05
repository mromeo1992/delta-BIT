# ft_tools.py
import json
import shutil
import zipfile
import requests
from pathlib import Path
import os
import random

FT_FOLDER = Path("/data/fine_tuning")

UPLOAD_DIR =Path("/data/uploads")
DATASETS_DIR = Path('/data/datasets')
STAGING_DIR = Path('/data/staging')
STAGING_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def validation_split(dataset_name: str, val_split: float = 0.1):
    dataset_path = DATASETS_DIR / dataset_name
    images_path = dataset_path / "imagesTr"
    labels_path = dataset_path / "labelsTr"


    image_files = sorted([f for f in os.listdir(images_path) if f.endswith(".nii") or f.endswith(".nii.gz")])
    #label_files = sorted([f for f in os.listdir(labels_path) if f.endswith(".nii") or f.endswith(".nii.gz")])


    num_samples = len(image_files)
    num_val_samples = int(num_samples * val_split)

    random.shuffle(image_files)

    val_image_files = [os.path.join(images_path, f) for f in image_files[:num_val_samples]]
    val_label_files = [os.path.join(labels_path, f) for f in image_files[:num_val_samples]]

    train_image_files = [os.path.join(images_path, f) for f in image_files[num_val_samples:]]
    train_label_files = [os.path.join(labels_path, f) for f in image_files[num_val_samples:]]

    dataset_cofing = {
        "name": dataset_name,
        "num_samples": num_samples,
        "num_train_samples": num_samples - num_val_samples,
        "num_val_samples": num_val_samples,
        "val_split": val_split,
        "train_image_files": train_image_files,
        "train_label_files": train_label_files,
        "val_image_files": val_image_files,
        "val_label_files": val_label_files,
    }
    config_path = dataset_path / "config.json"
    with open(config_path, "w") as f:
        json.dump(dataset_cofing, f, indent=4)

def send_notification(message: str, type: str = "info"):
    try:
        requests.post(
            "http://gui:8080/notify",
            json={"message": message, "type": type},
        )
    except requests.RequestException as e:
        print(f"Failed to send notification: {e}")

def check_dataset_structure(ds_name: str, min_samples: int = 10) -> bool:
    ds_folder = DATASETS_DIR / ds_name

    if not ds_folder.exists() or not ds_folder.is_dir():
        #send_notification(f"Dataset folder {ds_folder} does not exist", type="error")
        #raise ValueError(f"Dataset folder {ds_folder} does not exist")
        return False
    
    folder_to_check = ["imagesTr", "labelsTr"]
    for folder in folder_to_check:
        folder_path = ds_folder / folder
        if not folder_path.exists() or not folder_path.is_dir():
            #send_notification(f"Dataset folder {ds_folder} does not contain '{folder}' subfolder", type="error")
            #raise ValueError(f"Dataset folder {ds_folder} does not contain '{folder}' subfolder")
            return False
    img_list = sorted([ f for f in os.listdir(ds_folder / "imagesTr") if f.endswith(".nii") or f.endswith(".nii.gz") ])

    # Count the number of samples in the dataset
    sample_count = len(img_list)
    if sample_count < min_samples:
        #send_notification(f"Dataset {ds_name} contains only {sample_count} samples, which is less than the required minimum of {min_samples} samples.", type="error")
        #raise ValueError(f"Dataset {ds_name} contains only {sample_count} samples, which is less than the required minimum of {min_samples} samples.")
        return False
    
    for img in img_list:
        label_path = ds_folder / "labelsTr" / img
        if not label_path.exists():
            #send_notification(f"Mismatch found: Label file {label_path} does not exist for image {img}", type="error")
            #raise ValueError(f"Mismatch found: Label file {label_path} does not exist for image {img}")
            return False

    return True


def extract_dataset(zip_path: str, ds_name: str):
    ds_folder = DATASETS_DIR / ds_name
    ds_folder.mkdir(parents=True, exist_ok=False)

    with zipfile.ZipFile(zip_path) as zf:

        # Collect all non-empty paths
        members = [m for m in zf.infolist() if m.filename.strip("/")]

        # Determine the set of top-level directories/files
        top_levels = {
            Path(m.filename).parts[0]
            for m in members
            if Path(m.filename).parts
        }

        # Strip the first component only if there is exactly one
        # top-level directory in the archive.
        strip_root = len(top_levels) == 1

        for member in members:

            parts = Path(member.filename).parts

            if strip_root:
                parts = parts[1:]

            # Skip entries that become empty after stripping
            if not parts:
                continue

            destination = ds_folder.joinpath(*parts)

            if member.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
                continue

            destination.parent.mkdir(parents=True, exist_ok=True)

            with zf.open(member) as src, open(destination, "wb") as dst:
                shutil.copyfileobj(src, dst)

    check= check_dataset_structure(ds_name)

    if check:
        send_notification("Dataset uploaded", type="success")
        shutil.rmtree(STAGING_DIR)
        STAGING_DIR.mkdir(parents=True, exist_ok=True)
        validation_split(ds_name, val_split=0.1)
        return {"status": "done"}
    
    else:
        send_notification("Dataset upload failed", type="negative")
        shutil.rmtree(STAGING_DIR)
        STAGING_DIR.mkdir(parents=True, exist_ok=True)
        ds_folder = DATASETS_DIR / ds_name
        if ds_folder.exists():
            shutil.rmtree(ds_folder)    
        
        return {"status": "failed"}
