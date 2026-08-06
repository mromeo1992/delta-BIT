#data loader

import numpy as np
import nibabel as nib
from scipy import ndimage
import tensorflow as tf
from tensorflow import keras
from keras import backend as K
import os
import random
from script.utils.utils import get_cropping_border

cropping_border=get_cropping_border()


def padding(array,img_size):
    img_size_in=array.shape
    x_pad=int((img_size[0]-img_size_in[0])/2)
    x_pad_2=-x_pad
    if x_pad==0:
        x_pad=None
        x_pad_2=None
    y_pad=int((img_size[1]-img_size_in[1])/2)
    y_pad_2=-y_pad
    if y_pad==0:
        y_pad=None
        y_pad_2=None    
    z_pad=int((img_size[2]-img_size_in[2])/2)
    z_pad_2=-z_pad
    if z_pad==0:
        z_pad=None
        z_pad_2=None
    padded_array=np.zeros(img_size)
    padded_array[x_pad:x_pad_2,y_pad:y_pad_2,z_pad:z_pad_2]=array
    return padded_array


def resize_volume(volume, label, img_size, num_input):
    factors=[0.7,1.25]
    factor=random.uniform(factors[0],factors[1])
    #print(factor,'fattore')
    #resizing
    label=np.reshape(label, img_size)
    label = ndimage.zoom(label, (factor, factor, factor), order=1)
    new_shape=label.shape
    new_volume=np.zeros(np.append(new_shape,num_input))
    for i in range(num_input):
        new_volume[:,:,:,i] = ndimage.zoom(volume[:,:,:,i], (factor, factor, factor), order=1)

        if new_shape==img_size:
            '''new_volume[:,:,:,0]=np.array(new_volume[:,:,:,0]>0.5,dtype='uint8')'''
            return new_volume, np.expand_dims(label,3)
    
    else:
        #print(new_shape,'a')
        if factor< 1:
            for i in range(len(new_shape)):
                #print(i, new_shape[i])
                if np.logical_not((new_shape[i]-img_size[i]) % 2==0):
                    new_volume=np.insert(new_volume,0,0, axis=i)
                    label=np.insert(label,0,0,axis=i)
                #print(img.shape[i])
        #print(label.shape, img.shape)
            new_volume_2=np.zeros(np.append(img_size,num_input))
            for i in range(num_input):
                new_volume_2[:,:,:,i]=padding(new_volume[:,:,:,i],img_size)
            label=padding(label,img_size)
            label=np.expand_dims(label,3)
            #print(label.shape, 'b')
        else:
            new_volume_2=np.zeros(np.append(img_size,num_input))
            for i in range(num_input):
                new_volume_2[:,:,:,i]=cropping(new_volume[:,:,:,i],img_size)
            label=cropping(label,img_size)
            label=np.expand_dims(label,3)
            #print(label.shape, 'c')  
        '''new_volume_2[:,:,:,0]=np.array(new_volume_2[:,:,:,0]>0.5,dtype='uint8')'''    
        return new_volume_2, label

def gaussian_noise(img,img_size, num_input):
    shape=img_size
    for i in range(num_input):
        noise=np.random.normal(0,0.015, size=shape)
        img[:,:,:,i]=img[:,:,:,i]+noise[:,:,:]
        '''if i==0:
            img[:,:,:,i]=np.array(img[:,:,:,i]>0.8,dtype='uint8')'''
    return img


def cropping(img, img_size):
    dif=[]
    for i in range(3):
        if img.shape[i] != img_size[i]:
            a=img.shape[i]-img_size[i]
            if a % 2!=0:
                img=np.insert(img,-1,0,axis=i)
            a=img.shape[i]-img_size[i]
            dif.append([int(a/2),-int(a/2)])
        else:
            img=np.insert(img,-1,0,axis=i)
            dif.append([0,-1])
    img=img[dif[0][0]:dif[0][1],dif[1][0]:dif[1][1],dif[2][0]:dif[2][1]]
    return img


def traslation(volume, label,num_input):

    def traslazione (img,dx,dy,dz):
        img_t=np.roll(img,dx,axis=0)
        if dx<0:
            img_t[dx:,:,:]=0
        else:
            img_t[:dx,:,:]=0
        img_t=np.roll(img_t,dy,axis=1)
        if dy<0:
            img_t[:,dy:,:]=0
        else:
            img_t[:,:dy,:]=0
        img_t=np.roll(img_t,dz,axis=2)
        if dz<0:
            img_t[:,:,dz:]=0
        else:
            img_t[:,:,:dz]=0
        return img_t

    delta=np.linspace(-5,5,11,dtype='int32')
    dx=np.random.choice(delta)
    dy=np.random.choice(delta)
    dz=np.random.choice(delta)
    for i in range(0,num_input):
        volume[:,:,:,i]=traslazione(volume[:,:,:,i],dx,dy,dz)
    label[:,:,:,0]=traslazione(label[:,:,:,0], dx,dy,dz)
    


    return volume, label

def flipping(volume, label,num_input):
    def flip(image,scelta):

        if scelta==0:
            image=image[::-1,:,:,:]
            return image
        elif scelta==1:
            image=image[:,::-1,:,:]
            return image
        else:
            image=image[:,:,::-1,:]
            return image 

    pos=[0,1,2]
    scelta=np.random.choice(pos)
    volume=flip(volume,scelta)
    label=flip(label,scelta)



    return volume, label


def rotate(volume, label):
    """Rotazione del volume di qualche grado"""
    range_a=[-15,-10,-5,5,10,15]
    angle= random.choice(range_a)
    axes=random.choice([(0,1),(0,2),(1,2)])

    def scipy_rotate_volume(volume, angle, axes):
        max=np.max(volume)
        min=np.min(volume)
        volume = ndimage.rotate(volume, angle, axes, reshape=False)
        volume[volume < min]= min
        volume[volume > max]= max
        return volume
    
    augmented_volume=scipy_rotate_volume(volume,angle,axes)
    '''augmented_volume[:,:,:,0]=np.array(augmented_volume[:,:,:,0]>0.5, dtype='uint8')'''
    augmented_label=scipy_rotate_volume(label,angle,axes) 
    return augmented_volume, augmented_label

def random_data_augmentation(img, label,img_size, num_input):
    casi={
        '0':'nothing',
        '1':'rotate',
        '2':'rescale',
        '3':'gaussian_noise',
        '4':'flip',
        '5':'traslation'
    }
    cases=[int(d) for d in casi.keys()]
    scelta=random.choice(cases)
    #print(casi[str(scelta)])
    if scelta==0:
        return img, label
    if scelta ==1:
        return rotate(img, label)
    elif scelta == 2:
        return resize_volume(img, label,img_size,num_input)
    elif scelta==3:
        return gaussian_noise(img,img_size,num_input), label
    elif scelta==4:
        return flipping(img,label,num_input)
    else:
        return traslation(img, label,num_input)


def read_nifti_file(file_path):
    """Read and load volume"""
    #x_min, x_max, y_min, y_max, z_min, z_max = cropping_border['x_min'], cropping_border['x_max'], cropping_border['y_min'], cropping_border['y_max'], cropping_border['z_min'], cropping_border['z_max']
    return nib.load(file_path).get_fdata()#[x_min:x_max, y_min:y_max, z_min:z_max]

def process_scann(path):#, size_x, size_y, size_z):
    """Read an resize volume"""
    #lettura file
    volume = read_nifti_file(path)
    volume = (volume - np.min(volume)) / np.ptp(volume)
    return volume


class Talamo_train(keras.utils.Sequence):
    def __init__(self, batch_size,img_size,input_img_pahts,target_img_pahts,num_input,shuffle=True, data_aug=True):
        self.batch_size=batch_size
        self.img_size=img_size
        self.input_img_paths=input_img_pahts
        self.target_img_paths=target_img_pahts
        self.shuffle=shuffle
        self.data_aug=data_aug
        self.num_input=num_input
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
        for j, path in enumerate(batch_input_img_paths):
            img=process_scann(path)  #,[img_size[0],img_size[1], img_size[0]])
            if len(img.shape)==3:
                img=np.expand_dims(img,3)            
            x[j,:,:,:,:]=img
            #print(path)
        y=np.zeros((self.batch_size,)+self.img_size+(1,))
        for j, path in enumerate(batch_taeget_img_paths):
            #img=nib.load(path).get_fdata()
            img=process_scann(path)  #, [img_size[0],img_size[1], img_size[0]] )
            y[j]=np.expand_dims(img,3)
            #print(path)
        if self.data_aug:
            for j in range(len(x)):
                #x[j], y[j]= rotate(x[j], y[j])
                x[j], y[j]= random_data_augmentation(x[j],y[j], self.img_size, self.num_input)

        return x, y

    
def data_generator(dataset_config,img_size,batch_size, num_input, augmentation):

    train_input_img_paths = np.array(dataset_config["train_image_files"])
    train_target_img_paths = np.array(dataset_config["train_label_files"])

    val_input_img_paths = np.array(dataset_config["val_image_files"])
    val_target_img_paths = np.array(dataset_config["val_label_files"])

    print('Number of training samples:', len(train_target_img_paths))
    print('Number of validation samples:', len(val_target_img_paths))

    train_gen=Talamo_train(batch_size,img_size,train_input_img_paths, train_target_img_paths,num_input,data_aug=augmentation)
    #print("sono io il problema 2")
    val_gen=Talamo_train(1,img_size,val_input_img_paths,val_target_img_paths,num_input,shuffle=False,data_aug=False)
    #print("sono io il problema 2")
    return train_gen, val_gen


def data_test_loader(input_test_dir, target_test_dir,img_size,batch_size,num_input):
    input_img_pahts=sorted(
        [
            os.path.join(input_test_dir, fname)
            for fname in os.listdir(input_test_dir)
            if fname.endswith('.nii.gz')
        ]
    )

    target_img_pahts=sorted(
        [
            os.path.join(target_test_dir, fname)
            for fname in os.listdir(target_test_dir)
            if fname.endswith('.nii.gz')
        ]
    )

    print('Number of samples:', len(target_img_pahts))
    test_gen=Talamo_train(batch_size,img_size,input_img_pahts,target_img_pahts,num_input,shuffle=False,data_aug=False)
    return test_gen
