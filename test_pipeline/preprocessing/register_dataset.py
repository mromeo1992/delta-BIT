import os 
import sys
import json
import argparse
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../"))

from utils.json_maniging import reading_json, get_initialised_project


def reg_T1(T1, template, out_dir, dof=6):
    cmd='flirt -in '+T1+' -ref '+template+' -out '+out_dir+'/T1.nii.gz -omat '+out_dir+'/T1.mat '+'-dof '+str(dof)+' -interp nearestneighbour -v'
    print(cmd)
    #os.system(cmd)

def reg_dwi(dwi, T1, out_dir, dof=6):
    cmd='flirt -in '+dwi+' -ref '+T1+' -omat '+out_dir+'/dwi.mat '+'-dof '+str(dof)+' -interp nearestneighbour -v'
    print(cmd)
    #os.system(cmd)

def loop(dataset,template, out_dir):
    "Loop for image registration"

    for subject in dataset.keys():
        T1=dataset[subject]['T1 image']
        dwi=dataset[subject]['DWI image']
        reg_T1(T1, template,'./','T1')
        reg_dwi(dwi, T1, './','data')


templates=os.path.join(os.environ['DELTA_BIT'],'utils/templates')
templates=sorted([fil for fil in os.listdir(templates)
                  if fil.endswith('.nii.gz')])

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="With this script you can register your dataset."+
                                    "The minimum requirements dataset json file produced by write_json.py.",

                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-n", "--name", help="Project's name", required=True)
    parser.add_argument("-t", "--template", choices=templates, help="choose a template for registration (for testing pretrained models only MNI152_T1_1mm.nii.gz)", default="MNI152_T1_1mm.nii.gz")


    args = parser.parse_args()


    config = vars(args)

    name=config['name']
    json_path=get_initialised_project(name)
    print('Json file found in: '+json_path)
    json_object=reading_json(json_path)
    dataset=json_object['input files']['dataset']
    template=config['template']
    loop(dataset,template, None)
    