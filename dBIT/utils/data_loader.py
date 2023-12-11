#delta-BIT is a progragram for tractography prediction
#Copyright (C) 2023,  University of Palermo, department of Physics 
#and Chemistry, Palermo, Italy and National Institue of Nuclear Physics (INFN), Italy
#
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.



#data loader

import numpy as np
import nibabel as nib
import keras
import os

from dBIT.utils.data_augmentation import random_data_augmentation
default_box=os.path.join(os.environ['DELTA_BIT'],'dBIT/utils/cropping_border_default.npz')


def get_box(file_path):
    box=np.load(file_path)
    return box



def process_scann(path, box):#, size_x, size_y, size_z):
    """Read an resize volume"""
    if box:
        x_min, x_max = box['x_min'], box['x_max']
        y_min, y_max = box['y_min'], box['y_max']
        z_min, z_max = box['z_min'], box['z_max']
    else:
        x_min, x_max = None, None
        y_min, y_max = None, None
        z_min, z_max = None, None
    #lettura file
    volume = nib.load(path).get_fdata()[x_min:x_max,y_min:y_max,z_min:z_max,]
    shape=volume.shape
    if len(shape)==4:
        volume=(volume - np.min(volume,axis=(0,1,2))) / np.ptp(volume,axis=(0,1,2))
    else:
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
    def __init__(self, batch_size,img_size,input_img_pahts,header_paths ,subjects,num_input, box):
        self.batch_size=batch_size
        self.img_size=img_size
        self.input_img_paths=input_img_pahts
        self.header_paths=header_paths
        self.subjects=subjects
        self.num_input=num_input
        self.box=box
    
    def __len__(self):
        return len(self.input_img_paths)//self.batch_size
    

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
    
    def get_header(self, idx):
        i=idx*self.batch_size
        batch_input_img_paths=self.header_paths[i:i+self.batch_size]
        head=[]
        for path in batch_input_img_paths:
            head.append(nib.load(path).header)
        
        return head

    def get_affine(self, idx):
        i=idx*self.batch_size
        batch_input_img_paths=self.header_paths[i:i+self.batch_size]
        affine=[]
        for  path in batch_input_img_paths:
            affine.append(nib.load(path).affine)
        
        return affine
    
def data_generator_train(input_train_dir,target_train_dir,img_size,batch_size, num_input, val_size, box_path=default_box):
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


def data_generator_test_T1(json_object,batch_size=1,box_path=default_box):

    box=get_box(box_path)
    img_size=(box['x_max']-box['x_min'],box['y_max']-box['y_min'],box['z_max']-box['z_min'])

    dataset=json_object['processed files']['dataset']
    input_img_paths=[]
    subjects=list(dataset.keys())
    for sub in subjects:
        input_img_paths.append(dataset[sub]['T1 image'])


    print('Number of samples:', len(input_img_paths))
        
    test_gen=Talamo_test(batch_size,img_size,input_img_paths,input_img_paths, subjects,1,box)
    
    return test_gen


def data_gnerator_test_trac(json_object, num_input=11,batch_size=1,box_path=default_box):
    box=get_box(box_path)
    img_size=(box['x_max']-box['x_min'],box['y_max']-box['y_min'],box['z_max']-box['z_min'])

    dataset=json_object['processed files']['dataset']
    input_img_paths=[]
    header_paths=[]
    subjects=list(dataset.keys())
    for sub in subjects:
        input_img_paths.append(dataset[sub]['Network input'])#?
        header_paths.append(dataset[sub]['T1 image'])


    print('Number of samples:', len(input_img_paths))
        
    test_gen=Talamo_test(batch_size,img_size,input_img_paths,header_paths ,subjects,num_input,None)
    
    return test_gen
