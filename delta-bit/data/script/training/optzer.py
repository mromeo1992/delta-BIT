#This script contains the optimizer functions used for training the model. It includes Adam, AdamW, and SGD optimizers.
# It can be customized to include other optimizer functions as well. The optimizer functions are implemented as classes that inherit from keras.optimizers.Optimizer. 
# To make DeLTA-BIT capable of using other optimizer functions, you can add them to the OPTIMIZERS list in the optimizer_list.py file and implement them as classes that inherit from keras.optimizers.Optimizer in this file.
from keras import optimizers

adam_opt = optimizers.Adam
sgd_opt = optimizers.SGD