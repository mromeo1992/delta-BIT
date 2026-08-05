import numpy as np

from tensorflow import keras
import keras.backend as K

# FOR TRAINING/FT

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

# FOR EVAL PIPELINE

def get_cropping_border(cropping_border):
    data = np.load(cropping_border)
    return data

def precision(true, pred):
    tp=np.sum(true*pred)
    fp=np.sum((1-true)*pred)
    if tp + fp == 0:
        return 0.0
    return tp / (tp + fp)

# FOR TRAINING/FTUNING

def dice(y_true, y_pred, smooth=1e-7):
    #y_pred=K.cast(y_pred>0.5,'float32')
    #y_true=K.cast(y_true, 'int32')
    y_pred=K.flatten(y_pred)
    y_true=K.flatten(y_true)
    intersection=K.sum(y_pred*y_true)
    dice = (2*intersection+smooth) / (K.sum(y_true) + K.sum(y_pred) + smooth)
    return dice

def dice_coef(y_true, y_pred, smooth=1e-6):
    '''
    Dice coefficient for 10 categories. Ignores background pixel label 0
    Pass to model as metric during compile statement
    '''
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersect = K.sum(y_true*y_pred)
    denom = K.sum(y_true_f + y_pred_f)
    return (2. * intersect) / (denom + smooth)

def crossentropy(y_true,y_pred):
    # Clip values to prevent division by zero error
    return keras.losses.binary_crossentropy(y_true,y_pred)

def DiceBCELoss(targets, inputs, smooth=1e-6):    
       
    #flatten label and prediction tensors
    inputs = K.flatten(inputs)
    targets = K.flatten(targets)
    
    BCE =  keras.losses.binary_crossentropy(targets, inputs)
    intersection = K.sum(targets * inputs)
    dice_loss = 1 - (2*intersection + smooth) / (K.sum(targets) + K.sum(inputs) + smooth)
    Dice_BCE = BCE + dice_loss
    
    return Dice_BCE

def DiceBFocalLoss(targets, inputs, smooth=1e-6):    
       
    #flatten label and prediction tensors
    inputs = K.flatten(inputs)
    targets = K.flatten(targets)
    
    BFL =  keras.losses.BinaryFocalCrossentropy(True)(targets, inputs)

    intersection = K.sum(targets * inputs)
    dice_loss = 1 - (2*intersection + smooth) / (K.sum(targets) + K.sum(inputs) + smooth)
    Dice_BCE = BFL + dice_loss
    
    return Dice_BCE

def DiceBFocalTverskyLoss(true, pred,alpha=0.7 ,beta=0.3, eps=10E-7):    
       
    #flatten label and prediction tensors
    true = K.flatten(true)
    pred = K.flatten(pred)
    
    BFL =  keras.losses.BinaryFocalCrossentropy(True)(true, pred)

    intersection = K.sum(true * pred)+eps
    FP=K.sum((1-true)*pred)
    FN=K.sum((1-pred)*true)
    denom=intersection+alpha*FP+beta*FN+eps
    Tloss=1-2*intersection/denom
    
    return BFL+Tloss

def MSE_loss(y_true, y_pred):
    return keras.losses.MeanSquaredError()(y_true,y_pred)

def MSEdiceLoss(targets, inputs, smooth=1e-6):
    inputs = K.flatten(inputs)
    targets = K.flatten(targets)

    MSE=MSE_loss(targets, inputs)
    intersection = K.sum(targets * inputs)
    dice_loss = 1 - (2*intersection + smooth) / (K.sum(targets) + K.sum(inputs) + smooth)
    loss=MSE+dice_loss

    return loss
