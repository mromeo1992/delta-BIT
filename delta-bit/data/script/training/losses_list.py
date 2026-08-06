#This script contains the loss functions list used for training the model. It includes DiceBCELoss, DiceBFocalLoss, DiceBFocalTverskyLoss, OversizeLoss, and CombinedLoss.
# It can be customized to include other loss functions as well. The loss functions are implemented as classes that inherit from keras.losses.Loss. 
# To make DeLTA-BIT capable of using other loss functions, you can add them to the LOSSES list in this script file and implement them as classes that inherit from keras.losses.Loss in the losses.py file.

LOSSES = [
    "DiceBCELoss",
    "DiceBFocalLoss",
    "DiceBFocalTverskyLoss",
    "OversizeLoss",
    "CombinedLoss"
]