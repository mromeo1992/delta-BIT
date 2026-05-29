from fastapi import FastAPI
import json
import os
from script.GUI.viewer import get_image, return_image_size



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