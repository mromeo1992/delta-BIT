import nibabel as nib
import json
import os
import numpy as np
import sys
import argparse
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../"))

from utils.json_menaging import reading_json, get_initialised_project

dti_images=[
    'FA.nii.gz',
    'L1.nii.gz',
    'L2.nii.gz',
    'L3.nii.gz',
    'V1.nii.gz',
    'V2.nii.gz',
    'V3.nii.gz'
]

def make_dti_input(path_fold, output_fold, box):
    x_min, x_max=box['x_min'], box['x_max']
    y_min, y_max=box['y_min'], box['y_max']
    z_min, z_max=box['z_min'], box['z_max']

    img_size=(x_max-x_min, y_max-y_min, z_max-z_min)

#def make_T1_input










if __name__=='__main__':
    parser = argparse.ArgumentParser(description="With this script you can cut your dataset."+
                                    "The minimum requirements dataset json file produced by write_json.py, DWI preprocessing and registration.",

                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-n", "--name", help="Project's name", required=True)
    parser.add_argument("--box", help="Insert here the path of the bounding box you want to use (for test with pretrained models just use default choice)", default='pretraining box')
    #parser.add_argument("--tmp", action='store_true', help="Insert this flag if you want to keep temporary files")

    args = parser.parse_args()


    config = vars(args)
    name=config['name']

    box=config['box']
    if box=='pretraining box':
        box=os.path.join(os.environ['DELTA_BIT'],'utils','cropping_border_default.npz')
    box=np.load(box)

    json_object=get_initialised_project(name)
    json_object=reading_json(json_object)

    json_object['inputs']['networks_inputs_dir']=os.path.join(json_object['inputs']['output_dir'],'networks_inputs')
    output_dir=json_object['inputs']['networks_inputs_dir']
    if os.path.exists(output_dir):
        os.system('rm -r '+output_dir)
    os.mkdir(output_dir)
