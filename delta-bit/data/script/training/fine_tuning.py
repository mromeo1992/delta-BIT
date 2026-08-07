import json
import nibabel as nib
import numpy as np
import pandas as pd
import requests
from pathlib import Path

from script.load_model import load_model
import script.training.losses as lF
import script.training.optzer as OPT
from script.training.data_loader import data_generator

FT_FOLDER = Path("/data/fine_tuning")
MODELS_DIR = Path("/data/MODELS")
DATASETS_DIR = Path("/data/datasets")

def setup_ftmodel(config):
    model_name = config.get("name")

    

    model_folder = FT_FOLDER / model_name
    model_folder.mkdir(parents=True, exist_ok=True)

    config_path = model_folder / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

    ft_log_folder1 = model_folder / "logs_1step"
    ft_log_folder1.mkdir(parents=True, exist_ok=True)

    ft_log_folder2 = model_folder / "logs_2step"
    ft_log_folder2.mkdir(parents=True, exist_ok=True)

    checkpoint_folder = model_folder / "checkpoints"
    checkpoint_folder.mkdir(parents=True, exist_ok=True)






def finetuning(config):
    import tensorflow as tf
    from tensorflow import keras
    import keras.backend as K

    FIRST_UNFROZEN_LAYER = "conv3d_transpose"
    SECOND_UNFROZEN_LAYER = "conv3d_6"

    def freeze_layers(model, first_layer_to_unfreeze):
        
        found = False

        for layer in model.layers:

            if layer.name == first_layer_to_unfreeze:
                found = True

            layer.trainable = found

            if isinstance(layer, keras.layers.BatchNormalization):
                layer.trainable = False

        if not found:
            raise ValueError(
                f"Layer '{first_layer_to_unfreeze}' not found."
            )
        
        return model



    def fit_model(model, step):

        def set_optimizer(step):
            #########################
            # SET UP OPTIMIZER     #
            #########################
            #Customize the optimizer based on the configuration. You can add more optimizers to the opt_list in optimizer_list.py and implement them in optzer.py.
            if config["optimizer"]=="Adam":
                if step==1:
                    optimizer = OPT.adam_opt(learning_rate=config["learning_rate"])
                elif step==2:
                    optimizer = OPT.adam_opt(learning_rate=config["learning_rate"]*0.1)
            elif config["optimizer"]=="SGD":
                if step==1:
                    optimizer = OPT.sgd_opt(learning_rate=tf.keras.optimizers.schedules.PolynomialDecay(config["learning_rate"],1000,config["learning_rate"]*0.01))
                elif step==2:
                    optimizer = OPT.sgd_opt(learning_rate=tf.keras.optimizers.schedules.PolynomialDecay(config["learning_rate"]*0.1,1000,config["learning_rate"]*0.01*0.1))

            return optimizer
        
        def set_callbacks(step):
            ####################
            # SET UP CALLBACKS #
            ####################            
            if step==1:
                logs_dir = FT_FOLDER / config["name"] / "logs_1step"
                checkpoint_path = FT_FOLDER / config["name"] / "checkpoints" / "best_model_1step.h5"
            elif step==2:
                logs_dir = FT_FOLDER / config["name"] / "logs_2step"                
                checkpoint_path = FT_FOLDER / config["name"] / "checkpoints" / "best_model_2step.h5"
            
            tensorboard_cb = keras.callbacks.TensorBoard(log_dir=str(logs_dir))
            callbacks = [
                        keras.callbacks.ModelCheckpoint(
                            filepath=str(checkpoint_path),
                            save_weights_only=True,
                            monitor="val_dice",
                            mode="max",
                            save_best_only=True
                        )
                        ]
            patience = int(config.get("epochs")*0.1)  # Set patience to 10% of the total epochs

            early_stop = keras.callbacks.EarlyStopping(
                monitor="val_dice",
                mode="max",
                patience=patience,
                restore_best_weights=True
                )
            
            callbacks.append(tensorboard_cb)
            callbacks.append(early_stop)
            return callbacks
            
        
        optimizer = set_optimizer(step)
        callbacks = set_callbacks(step)
        

        model.compile(optimizer=optimizer, loss=lossF, metrics=[monitoring_metric])
        
        history = model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=epochs,
            callbacks=callbacks
        )
        
        return history, model

    ###############
    # LOAD CONFIG #
    ###############

    setup_ftmodel(config)

    model_config = config["model"]["meta"]
    model_config["model"]["path_model"] = str(MODELS_DIR / config["model"]["name"]/"model.h5")
    epochs = config["epochs"]

    img_size = tuple(model_config["model"]["img_size"])
    num_input = model_config["model"]["num_input"]
    batch_size = config["batch_size"]
    augmentation = config["augmentation"]

    print(f"Model config: {model_config}")


    ###############
    # LOAD LOSS   #
    ###############

    lossF = getattr(lF, config["loss"])()   
    monitoring_metric = getattr(lF, 'Dice')()

    
    ################
    # SET UP MODEL #
    ################

    K.clear_session()
    
    model = load_model(model_config["model"])
    model.summary()

    dataset_config = DATASETS_DIR / config["dataset"] /"config.json"
    with open(dataset_config, "r") as f:
        dataset_config = json.load(f)

    train_gen, val_gen = data_generator(dataset_config,img_size,batch_size, num_input, augmentation)

    ###################
    # FREEZE LAYERS #
    ###################

    model = freeze_layers(model, FIRST_UNFROZEN_LAYER)

    print("Starting fine tuning first step...")
    hs, model2 = fit_model(model, step=1)

    hist_df = pd.DataFrame(hs.history)
    # save to json:  
    hist_json_file = FT_FOLDER / config["name"] / "history_1step.json"
    with open(hist_json_file, mode='w') as f:
        hist_df.to_json(f)

    model2 = freeze_layers(model2, SECOND_UNFROZEN_LAYER)
    
    print("Starting fine tuning second step...")
    hs2, model3 = fit_model(model2, step=2)

    hist_df = pd.DataFrame(hs2.history)
    # save to json:  
    hist_json_file = FT_FOLDER / config["name"] / "history_2step.json"
    with open(hist_json_file, mode='w') as f:
        hist_df.to_json(f)


    return {"status": "model loaded"}