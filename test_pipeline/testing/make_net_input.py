import nibabel as nib
import json
import os
import numpy as np
import sys
import argparse
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.environ['DELTA_BIT']))

from utils.json_menaging import reading_json, get_initialised_project
from test_pipeline.preprocessing.write_json import write_json
from utils.data_loader import get_box

dti_images=[
    'FA.nii.gz',
    'L1.nii.gz',
    'L2.nii.gz',
    'L3.nii.gz',
    'V1.nii.gz',
    'V2.nii.gz',
    'V3.nii.gz'
]

def make_net_input(dataset_file, num_inputs=11):
    
    box=dataset_file['inputs']['bounding box file']
    box=get_box(box)
    x_min, x_max=box['x_min'], box['x_max']
    y_min, y_max=box['y_min'], box['y_max']
    z_min, z_max=box['z_min'], box['z_max']
    img_size=(x_max-x_min, y_max-y_min, z_max-z_min)

    dataset=dataset_file['processed files']['dataset']
    output_dir=dataset_file['inputs']['networks_inputs_dir']
    subjects=dataset.keys()

    output_dataset=[]

    print('\n\nStart processing images\n\n')
    for sb in subjects:
        output_img=np.zeros(img_size+(num_inputs,))
        tal=dataset[sb]['Thalamus']
        tal=nib.load(tal)
        affine=tal.affine
        tal=tal.get_fdata()[x_min:x_max,y_min:y_max,z_min:z_max]
        output_img[:,:,:,0]=tal
        FA=os.path.join(dataset[sb]['DTI fold'],dti_images[0])
        FA=nib.load(FA).get_fdata()[x_min:x_max,y_min:y_max,z_min:z_max]
        FA=(FA-np.min(FA))/np.ptp(FA)
        output_img[:,:,:,1]=FA

        eingenVal=dti_images[1:4]
        eingenVec=dti_images[-3:]
        for i in range(3):
            eval=os.path.join(dataset[sb]['DTI fold'],eingenVal[i])
            eval=nib.load(eval).get_fdata()[x_min:x_max,y_min:y_max,z_min:z_max]

            evec=os.path.join(dataset[sb]['DTI fold'],eingenVec[i])
            evec=nib.load(evec).get_fdata()[x_min:x_max,y_min:y_max,z_min:z_max,:]
            for j in range(3):
                im=eval*evec[:,:,:,j]
                im=(im-np.min(im))/np.ptp(im)                
                output_img[:,:,:,2+3*i+j]=im
        
        to_save=nib.Nifti1Image(output_img,affine)
        fname=os.path.join(output_dir, sb+'.nii.gz')
        nib.save(to_save,fname)
        output_dataset.append([sb,fname])
        print('Subject '+sb+' done\n')

    print("\n\nAll subject are completed\n\n")
    
    print("Saving json file\n\n")
    if "Make inputs" not in dataset_file['inputs']['steps']:
        dataset_file['inputs']['steps'].append("Make inputs")
    for sb, inp in output_dataset:
        dataset_file['processed files']['dataset'][sb]['Network input']=inp

    jsonfile=os.path.join(dataset_file['inputs']['output_dir'],'dataset.json')
    write_json(dataset_file,jsonfile)

    cmd='cp '+jsonfile+' '+dataset_file['inputs']['project_file']
    print('\nCoping report json in '+dataset_file['inputs']['project_file'])
    print('\n'+cmd)
    os.system(cmd)
    
    print('Done!')

    





def main():
    parser = argparse.ArgumentParser(description="With this script you can cut your dataset."+
                                    "The minimum requirements dataset json file produced by write_json.py, DWI preprocessing and registration.",

                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-n", "--name", help="Project's name", required=True)

    args = parser.parse_args()


    config = vars(args)
    name=config['name']
    json_object=get_initialised_project(name)
    json_object=reading_json(json_object)

    json_object['inputs']['networks_inputs_dir']=os.path.join(json_object['inputs']['output_dir'],'networks_inputs')
    output_dir=json_object['inputs']['networks_inputs_dir']
    if os.path.exists(output_dir):
        os.system('rm -r '+output_dir)
    os.mkdir(output_dir)

    make_net_input(json_object)





if __name__=='__main__':
    main()

