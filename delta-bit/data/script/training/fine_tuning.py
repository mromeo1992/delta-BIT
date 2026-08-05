from tensorflow import keras
import keras.backend as K

import json
import nibabel as nib
import numpy as np
import requests
from pathlib import Path

from script.load_model import load_model

FT_FOLDER = Path("/data/fine_tuning")
MODELS_DIR = Path("/data/MODELS")
DATASETS_DIR = Path("/data/datasets")

def setup_ftmodel(config):
    model_name = config.get("name")

    
    '''requests.post(
        "http://gui:8080/notify",
        json={"message": f"Fine-tuning request received with model name: {model_name}"},
    ) '''   

    model_folder = FT_FOLDER / model_name
    model_folder.mkdir(parents=True, exist_ok=True)

    config_path = model_folder / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

    ft_log_folder = model_folder / "logs"
    ft_log_folder.mkdir(parents=True, exist_ok=True)



def finetuning(config):

    '''requests.post(
        "http://gui:8080/notify",
        json={"message": f"Fine-tuning request received with config: {config}"},
    )'''

    ###############
    # LOAD CONFIG #
    ###############

    setup_ftmodel(config)

    model_config = config["model"]["meta"]
    model_config["model"]["path_model"] = str(MODELS_DIR / config["model"]["name"]/"model.h5")
    print(f"Model config: {model_config}")


    ################
    # SET UP MODEL #
    ################

    K.clear_session()
    model = load_model(model_config["model"])
    model.summary()

    return {"status": "model loaded"}