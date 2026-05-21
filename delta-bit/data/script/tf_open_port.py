from fastapi import FastAPI
import json
import os



app2 = FastAPI()

@app2.post("/predict")
def predict():
    #predizione
    conf_img = "data/config/config.json"
    config_img_data = json.load(open(conf_img))
    from .predict_vim import predict_vim
    predict_vim(config_img_data)