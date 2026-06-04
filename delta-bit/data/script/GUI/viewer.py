import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def return_image_size(path: str, axis : str):
    volume = nib.load(path).get_fdata()
    if axis=="axial":
        #z = volume.shape[2] // 2
        imax = volume.shape[2]
    elif axis=="coronal":
        #y = volume.shape[1] // 2
        imax = volume.shape[1]
    elif axis == "sagittal":
        #x = volume.shape[0] // 2
        imax = volume.shape[0]
    
    return imax


def get_image(path: str, axis : str, sl : int):
    #requests.post(
    #        'http://gui:8080/notify',
    #        json={'message': 'Selected axis : {}'.format(axis)}
    #    )        

    volume = nib.load(path).get_fdata()
    if axis=="axial":
        #z = volume.shape[2] // 2
        slice_img = volume[:, :, sl]
    elif axis=="coronal":
        #y = volume.shape[1] // 2
        slice_img = volume[:, sl, :]
    elif axis == "sagittal":
        #x = volume.shape[0] // 2
        slice_img = volume[sl, :, :]

    fig, ax = plt.subplots(figsize=(10,10), dpi=150)

    ax.imshow(np.rot90(slice_img), cmap='gray')
    ax.set_aspect('equal')
    ax.axis('off')

    buf = BytesIO()
    plt.savefig(buf, format='png', pad_inches=0)

    plt.close(fig)    

    return base64.b64encode(buf.getvalue()).decode()