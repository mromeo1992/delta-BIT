# List of available optimizers. 
# To make DeLTA-BIT capable of using other optimizer functions, you can add them to the opt_list in this script file and implement them as classes that inherit from keras.optimizers.Optimizer in the optzer.py file.
OPTIMIZERS = ["Adam",
            "SGD"]