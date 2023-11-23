#data loader

import numpy as np
import nibabel as nib
import keras
import os
from data_augmentation import random_data_augmentation

def get_box(file_path):
    box=np.load(file_path)
    return box



def process_scann(path, box):#, size_x, size_y, size_z):
    """Read an resize volume"""

    x_min, x_max = box['x_min'], box['x_max']
    y_min, y_max = box['y_min'], box['y_max']
    z_min, z_max = box['z_min'], box['z_max']
    #lettura file
    volume = nib.load(path).get_fdata()[x_min:x_max,y_min:y_max,z_min:z_max,]
    volume = (volume - np.min(volume)) / np.ptp(volume)
    return volume


class Talamo_train(keras.utils.Sequence):
    def __init__(self, batch_size,img_size,input_img_pahts,target_img_pahts,num_input, box,shuffle=True, data_aug=True):
        self.batch_size=batch_size
        self.img_size=img_size
        self.input_img_paths=input_img_pahts
        self.target_img_paths=target_img_pahts
        self.shuffle=shuffle
        self.data_aug=data_aug
        self.num_input=num_input
        self.box=box
        self.on_epoch_end()
    
    def __len__(self):
        return len(self.target_img_paths)//self.batch_size
    

    def on_epoch_end(self):
        randomize=np.arange(len(self.target_img_paths))
        np.random.shuffle(randomize)
        if self.shuffle:
            self.input_img_paths=self.input_img_paths[randomize]
            self.target_img_paths=self.target_img_paths[randomize]

    def __getitem__(self, idx):
        i=idx*self.batch_size
        batch_input_img_paths=self.input_img_paths[i:i+self.batch_size]
        batch_taeget_img_paths=self.target_img_paths[i:i+self.batch_size]
        x=np.zeros((self.batch_size,)+self.img_size+(self.num_input,))
        if self.num_input ==1:
            for j, path in enumerate(batch_input_img_paths):
                img=process_scann(path,self.box)
                x[j]=np.expand_dims(img,3)
        else:
            for j, path in enumerate(batch_input_img_paths):
                img=process_scann(path, self.box) 
                x[j,:,:,:,:]=img
        y=np.zeros((self.batch_size,)+self.img_size+(1,))
        for j, path in enumerate(batch_taeget_img_paths):
            img=process_scann(path, self.box)
            y[j]=np.expand_dims(img,3)
        if self.data_aug:
            for j in range(len(x)):
                x[j], y[j]= random_data_augmentation(x[j],y[j], self.img_size, self.num_input)

        return x, y
    
class Talamo_test(keras.utils.Sequence):
    def __init__(self, batch_size,img_size,input_img_pahts,num_input, box):
        self.batch_size=batch_size
        self.img_size=img_size
        self.input_img_paths=input_img_pahts
        self.num_input=num_input
        self.box=box
    
    def __len__(self):
        return len(self.target_img_paths)//self.batch_size
    

    def __getitem__(self, idx):
        i=idx*self.batch_size
        batch_input_img_paths=self.input_img_paths[i:i+self.batch_size]
        x=np.zeros((self.batch_size,)+self.img_size+(self.num_input,))
        if self.num_input ==1:
            for j, path in enumerate(batch_input_img_paths):
                img=process_scann(path,self.box) 
                x[j]=np.expand_dims(img,3)
        else:
            for j, path in enumerate(batch_input_img_paths):
                img=process_scann(path, self.box)
                x[j,:,:,:,:]=img
        return x

    
def data_generator_train(input_train_dir,target_train_dir,img_size,batch_size, num_input, val_size, box_path='./cropping_border_default.npz'):
    box=get_box(box_path)

    input_img_pahts=sorted(
        [
            os.path.join(input_train_dir, fname)
            for fname in os.listdir(input_train_dir)
            if fname.endswith('.nii.gz')
        ]
    )

    target_img_pahts=sorted(
        [
            os.path.join(target_train_dir, fname)
            for fname in os.listdir(target_train_dir)
            if fname.endswith('.nii.gz')
        ]
    )

    print('Number of samples:', len(target_img_pahts))

    val_samples=val_size
    val_index=np.arange(len(target_img_pahts))
    val_index=np.random.choice(val_index,val_samples,False)
    val_index=np.sort(val_index)
    val_input_img_paths=np.array(input_img_pahts)[val_index]
    val_target_img_paths=np.array(target_img_pahts)[val_index]
    train_input_img_paths=np.setdiff1d(input_img_pahts,val_input_img_paths)
    train_target_img_paths=np.setdiff1d(target_img_pahts,val_target_img_paths)

    train_gen=Talamo_train(batch_size,img_size,train_input_img_paths, train_target_img_paths,num_input,box)
    val_gen=Talamo_train(1,img_size,val_input_img_paths,val_target_img_paths,num_input,box,shuffle=False,data_aug=False)
    return train_gen, val_gen


def data_generator_test(json_object,num_input,batch_size=1,box_path='./cropping_border_default.npz'):

    box=get_box(box_path)
    img_size=(box['x_max']-box['x_min'],box['y_max']-box['y_min'],box['z_max']-box['z_min'])

    print('Number of samples:', len(input_img_pahts))
        
    test_gen=Talamo_test(batch_size,img_size,input_img_pahts,num_input,box)
    
    return test_gen
