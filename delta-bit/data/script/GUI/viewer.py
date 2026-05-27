import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def get_middle_slice(path: str):

    volume = nib.load(path).get_fdata()

    z = volume.shape[2] // 2
    slice_img = volume[:, :, z]

    fig, ax = plt.subplots(figsize=(10,10), dpi=150)

    ax.imshow(np.rot90(slice_img), cmap='gray')
    ax.set_aspect('equal')
    ax.axis('off')

    buf = BytesIO()
    plt.savefig(buf, format='png', pad_inches=0)

    plt.close(fig)    

    return base64.b64encode(buf.getvalue()).decode()