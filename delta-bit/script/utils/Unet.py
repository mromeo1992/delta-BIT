from tensorflow import keras
from keras import layers
from keras import regularizers
import numpy as np


def generator(img_size, num_input, n_liv=4, n_can_in=16, n_can_out=1, weight_decay=1e-04):
    k_regularizer=regularizers.l2(weight_decay)
    def downblock(x,filter,kernel_size,stride=1):
        block=layers.Conv3D(filter, kernel_size,strides=stride, padding='same', kernel_regularizer=k_regularizer, kernel_initializer='random_normal', use_bias=False)(x)
        block=layers.BatchNormalization()(block)
        skip=block
        block=layers.LeakyReLU()(block)

        block=layers.Conv3D(filter, kernel_size,strides=1, padding='same', kernel_regularizer=k_regularizer, kernel_initializer='random_normal', use_bias=False)(block)
        block=layers.BatchNormalization()(block)
        block=layers.Add()([block, skip])
        block=layers.LeakyReLU()(block)
        #block=layers.SpatialDropout3D(0.2)(block)
        return block

    def collo_bottiglia(previus_layer, n_filters, kernel_size, stride):
        block=layers.Conv3D(n_filters, kernel_size,strides=stride, padding='same', kernel_regularizer=k_regularizer, kernel_initializer='random_normal', use_bias=False)(previus_layer)
        block=layers.BatchNormalization()(block)
        skip=block
        block=layers.LeakyReLU()(block)
        block=layers.Conv3D(n_filters, kernel_size,strides=1, padding='same', kernel_regularizer=k_regularizer, kernel_initializer='random_normal', use_bias=False)(block)
        block=layers.BatchNormalization()(block)
        block=layers.Add()([block, skip])
        block=layers.SpatialDropout3D(0.1)(block)
        return block


    def upblock(x, x_left,filter, kernel_size, stride=1,outputs_pad=None):
        x=layers.Conv3DTranspose(filter, kernel_size, strides=stride, output_padding=outputs_pad, padding='same', kernel_regularizer=k_regularizer, kernel_initializer='random_normal', use_bias=False)(x)
        x=layers.BatchNormalization()(x)
        skip=x
        x=layers.LeakyReLU()(x)
        merge=layers.Concatenate(axis=-1)([x_left,x])

        x=layers.Conv3DTranspose(filter, kernel_size, strides=1, padding='same', kernel_regularizer=k_regularizer, kernel_initializer='random_normal', use_bias=False)(merge)
        x=layers.BatchNormalization()(x)
        x=layers.Add()([x, skip])
        x=layers.LeakyReLU()(x)
        #x=layers.SpatialDropout3D(0.2)(x)
        return x

    keras.backend.clear_session()
    #output padding
    out_pad=[]
    prev=np.array(img_size)
    for i in range(n_liv-1):
        resolution=np.array(img_size)//2**(i)
        if i!=0:
            resolution=resolution+prev%2
        prev=resolution
        pad=[]
        for j in range(3):
            if resolution[j]%2==0:
                pad.append(1)
            else:
                pad.append(0)
        out_pad.insert(0,pad)

    
        

    
    #network
    inputs=keras.Input(shape=img_size+(num_input,))
    skip=[]     
    for i in range(0,n_liv-1):
        if i==0:
            outputs=downblock(inputs,n_can_in*2**i,3,1)
        else:
            outputs=downblock(outputs,n_can_in*2**i,3,2)
        skip.insert(0,outputs)
    
    outputs=collo_bottiglia(outputs,n_can_in*2**(n_liv-1),3,2)


    for i in range(n_liv-1):
        #print(out_pad[i])
        outputs=upblock(outputs,skip[i],n_can_in*2**(n_liv-i-2),3, 2,outputs_pad=out_pad[i])

    outputs=layers.Conv3D(n_can_out,3,padding='same', activation='sigmoid')(outputs)

    model=keras.Model(inputs, outputs)
    return model



