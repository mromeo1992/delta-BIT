from utils.Unet import generator
import keras

def from_model(config):
    path=config['path_model']
    model=keras.models.load_model(path,compile=False)
    return model

def from_weights(config):
    path=config['path_model']
    img_size=config['img_size']
    num_input=config['num_input']
    n_can_in=config['n_can_in']
    model=generator(img_size=img_size, num_input=num_input, n_can_in=n_can_in)
    model.load_weights(path)
    return model

def load_model(config):
    try:
        model=from_model(config)
    except:
        model=from_weights(config)
    return model