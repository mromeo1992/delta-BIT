from fastapi import FastAPI
import json
import os
from script.GUI.viewer import get_middle_slice



app2 = FastAPI()

@app2.post("/predict")
def predict():
    #predizione
    conf_img = "/data/config/config.json"
    config_img_data = json.load(open(conf_img))
    from .predict_vim import predict_vim
    predict_vim(config_img_data)

@app2.post('/view')
def view_image(data: dict):

    path = data["path"]

    print(path)
    
    img_b64 = get_middle_slice(path)

    return {
        "image": img_b64
    }