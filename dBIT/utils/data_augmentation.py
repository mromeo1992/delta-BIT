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

import numpy as np
import random
from scipy import ndimage



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
    factors=[0.7,1.3]
    factor=random.uniform(factors[0],factors[1])
    #print(factor,'fattore')
    #resizing
    label=np.reshape(label, img_size)
    label = np.array(ndimage.zoom(label, (factor, factor, factor), order=1)>0.5,dtype='int32' )
    new_shape=label.shape
    new_volume=np.zeros(np.append(new_shape,num_input))
    for i in range(num_input):
        new_volume[:,:,:,i] = ndimage.zoom(volume[:,:,:,i], (factor, factor, factor), order=1)

    if new_shape==img_size:
        new_volume[:,:,:,0]=np.array(new_volume[:,:,:,0]>0.5,dtype='uint8')
        return new_volume, np.expand_dims(label,3)
    
    else:
        #print(new_shape,'a')
        if factor< 1:
            for i in range(len(new_shape)):
                #print(i, new_shape[i])
                if np.logical_not(new_shape[i] % 2==0):
                    new_volume=np.insert(new_volume,-1,0, axis=i)
                    label=np.insert(label,-1,0,axis=i)
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
        new_volume_2[:,:,:,0]=np.array(new_volume_2[:,:,:,0]>0.5,dtype='uint8')    
        return new_volume_2, label

def gaussian_noise(img,img_size, num_input):
    shape=img_size
    for i in range(num_input):
        noise=np.random.normal(0,0.025, size=shape)
        img[:,:,:,i]=img[:,:,:,i]+noise[:,:,:]
        if i==0:
            img[:,:,:,i]=np.array(img[:,:,:,i]>0.8,dtype='uint8')
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
    augmented_volume[:,:,:,0]=np.array(augmented_volume[:,:,:,0]>0.5, dtype='uint8')
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