import pandas as pd
import datetime
import json

from tensorflow import keras
import keras.backend as K

from app.utils.paths import *
from app.utils.makedirs import make_model_dirs
from app.database import dbase
import app.src.data_loader as data_loader
import app.src.utils as utils
import app.src.losses as lF
#from utils import *

print("CLEARING SESSION")

K.clear_session()

###############
# LOAD CONFIG #
###############

print("LOADING CONFIG FILE")

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)
print(json.dumps(config, indent=2))

# Maybe it's better to use the config directly instead of assigning variables

input_train_dir = config["paths"]["ftune_imagesTr"]
target_train_dir = config["paths"]["ftune_labelsTr"]

#pred_dir = config["paths"]["predictions_dir"]

model_path = config["paths"]["path_model"]

model_arch = config["model"]["architecture"]
img_size = tuple(config["model"]["img_size"])
num_input = config["model"]["num_input"]
batch_size = config["model"]["batch_size"]
val_size = config["model"]["val_size"]
max_epochs = config["model"]["max_epochs"]
patience = config["model"]["patience"]
learning_rate = config["model"]["learning_rate"]

loss_name = config["model"]["loss"]
loss_cls = getattr(lF, config["model"]["loss"])
loss_kwargs = config["model"].get("loss_args", {})
lossF = loss_cls(**loss_kwargs)

metrics_list = config["model"]["compile_w_metrics"]
metrics = [getattr(utils, m) for m in metrics_list]

watch_metric = config["watch_metric"]

first_layer_to_unfreeze = config["model"]["freeze2layer"]

weights_only = config["model"]["save_weights_only"]

mode = "min" if "loss" in watch_metric else "max"

################
# SET UP MODEL #
################

# Set model ID
model_id=f"model_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Make experiment folders
dirs = make_model_dirs(model_id)

model=keras.models.load_model(model_path, compile=False)

# Freeze layers
model = utils.freeze_layers(model=model, first_layer_to_unfreeze=first_layer_to_unfreeze)

optimizer=keras.optimizers.Adam(learning_rate)

# Set up combined loss
oversize_loss = lF.OversizeLoss(weight=1e-4)
comb_loss = lF.CombinedLoss(dice_loss=lossF, oversize_loss=oversize_loss)

# Use the module load_model that you took from Mattia
model.compile(optimizer=optimizer, loss=comb_loss, metrics=metrics)

checkpoint_path = dirs["checkpoints_dir"] / "best_{epoch:02d}.keras"

callbacks = [
    keras.callbacks.ModelCheckpoint(
        filepath=str(checkpoint_path),
        save_weights_only=weights_only,
        monitor=watch_metric,
        mode=mode,
        save_best_only=True
    )
]

# run in terminal with:
# tensorboard --logdir=./logs
#open browser to see real-time logs
tensorboard_cb = keras.callbacks.TensorBoard(log_dir=str(dirs["logs_dir"]))
callbacks.append(tensorboard_cb)

early_stop = keras.callbacks.EarlyStopping(
    monitor=watch_metric,
    mode=mode,
    patience=patience,
    restore_best_weights=True
    )
callbacks.append(early_stop)

####################
# TRAINING/FTUNING #
####################

# Load data
train_gen, val_gen=data_loader.data_generator(input_train_dir,target_train_dir,img_size,batch_size,num_input,val_size)
print("LOADED TRAINING DATA")

# Train/ftune
history=model.fit(
    train_gen,
    epochs=max_epochs,
    validation_data=val_gen,
    callbacks=callbacks)

########################
# SAVE EXPERIMENT DATA #
########################

# Save model
model_to_save = dirs["model_dir"] / "latest_model.keras"
model.save(model_to_save)

# Save history to json:
hist_df = pd.DataFrame(history.history)
hist_json_file = dirs["model_dir"] / "history.json"
with open(hist_json_file, mode='w') as f:
    hist_df.to_json(f)

# Save model's metadata
metadata = {
    "model_id": model_id,
    "parent_model": model_path,
    "architecture": model_arch,
    "train_dataset": input_train_dir,
    "loss":loss_name,
    "metric":metrics_list,
    "epochs_trained":len(hist_df),
    "learning_rate":learning_rate,
    "batch_size": batch_size,
    "img_size": img_size,
    "loss_args": loss_kwargs,
    "freeze2layer": first_layer_to_unfreeze,
    "max_epochs": max_epochs,
    "patience": patience
}

metadata_json_path = dirs["model_dir"] / "metadata.json"

with open(metadata_json_path, "w") as f:
    json.dump(metadata, f, indent=2)

# Save model entry in database
with dbase.TrackerDB(DB_PATH) as db:
    db.init_db()

    db.create_model(
        model_id,
        parent_model_id=model_path,
        train_dataset=input_train_dir,
        architecture=model_arch
    )

print("FINE-TUNING COMPLETE")
