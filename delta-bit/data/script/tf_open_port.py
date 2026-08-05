from fastapi import FastAPI
import json
import os
from script.GUI.viewer import get_image, return_image_size
from pathlib import Path
from script.ft_tools import setup_ftmodel
from script.utils.tensorboard_manager import TensorBoardManager

FT_FOLDER = Path("/data/fine_tuning")

tb_manager = TensorBoardManager()

app2 = FastAPI()

@app2.post("/predict")
def predict():
    #predizione
    conf_img = "/data/config/config.json"
    config_img_data = json.load(open(conf_img))
    from .predict_vim import predict_vim
    predict_vim(config_img_data)


@app2.post("/imsize")
def imsize(data: dict):
    path = data["path"]
    axis= data["axis"]

    imax= return_image_size(path , axis)
    return imax


@app2.post('/view')
def view_image(data: dict):

    path = data["path"]
    axis= data["axis"]
    sl = data["slice"]

    print(path)
    
    img_b64 = get_image(path,axis,sl)

    return {
        "image": img_b64
    }

@app2.post('/fine_tuning')
def fine_tuning(data: dict):
    name = data["name"]
    print("Fine-tuning request received with data:", data)
    model_folder= FT_FOLDER / name
    setup_ftmodel(data)

    return str(model_folder)


@app2.post("/tensorboard/start")
def start_tensorboard():

    started = tb_manager.start(
        FT_FOLDER
    )

    return {
        "running": True,
        "started": started
    }


@app2.post("/tensorboard/stop")
def stop_tensorboard():

    stopped = tb_manager.stop()

    return {
        "running": False,
        "stopped": stopped
    }


@app2.get("/tensorboard/status")
def tensorboard_status():

    return {
        "running": tb_manager.is_running()
    }