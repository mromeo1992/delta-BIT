# ft_tools.py
import json
import shutil
import zipfile
import requests
from pathlib import Path
import os

FT_FOLDER = Path("/data/fine_tuning")

UPLOAD_DIR = "/data/uploads"
DATASETS_DIR = Path('/data/datasets')
STAGING_DIR = Path('/data/staging')


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

    requests.post(
        "http://gui:8080/notify",
        json={"message": "Dataset uploaded"},
    )

    shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    return {"status": "done"}



def setup_ftmodel(config):
    model_name = config.get("name")

    if not model_name:
        raise ValueError("Model name is required")
    
    requests.post(
        "http://gui:8080/notify",
        json={"message": f"Fine-tuning request received with model name: {model_name}"},
    )    

    model_folder = FT_FOLDER / model_name
    model_folder.mkdir(parents=True, exist_ok=True)

    config_path = model_folder / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

    ft_log_folder = model_folder / "logs"
    ft_log_folder.mkdir(parents=True, exist_ok=True)

    cmd=f"tensorboard --logdir {ft_log_folder}"
    os.system(cmd)


    return str(model_folder)