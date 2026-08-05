import numpy as np




def get_cropping_border():
    cropping_border='/data/script/utils/cropping_border_default.npz'
    data = np.load(cropping_border)
    return data

def precision(true, pred):
    tp=np.sum(true*pred)
    fp=np.sum((1-true)*pred)
    if tp + fp == 0:
        return 0.0
    return tp / (tp + fp)

def recall(true, pred):
    tp=np.sum(true*pred)
    fn=np.sum(true*(1-pred))
    if tp + fn == 0:
        return 0.0
    return tp / (tp + fn)