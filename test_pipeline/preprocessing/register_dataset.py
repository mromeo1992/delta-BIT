import os 
import sys
import json
import argparse
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../"))

from utils.json_menaging import reading_json, get_initialised_project
from test_pipeline.preprocessing.write_json import write_json


def reg_T1_to_mni(T1, template,script, out_dir):
    print('\n\nStart T1 registration\n\n')
    tmp_fold=os.path.join(out_dir,'tmp')
    cmd='sh '+script+' --workingdir='+tmp_fold+' --in='+T1+'  --ref='+template+' --out='+out_dir+'/T1 --omat='+tmp_fold+'/T1_acpc.mat'
    print(cmd)
    os.system(cmd)
    print('\n\nT1 registration done\n\n')

def reg_dti(dti_fold, T1, T1_reg, out_dir):
    print('\n\nStart DTI registration\n\n')
    tmp_fold=os.path.join(out_dir,'tmp')
    dti_images=sorted([fil for fil in os.listdir(dti_fold)])
    FA=os.path.join(dti_fold,dti_images[0])
    #reg 2D
    cmd1='flirt -in '+FA+' -ref '+T1+' -out '+tmp_fold+'/FA1.nii.gz -omat '+tmp_fold+'/dwi2T1_2D.mat -2D -v'
    print(cmd1)
    os.system(cmd1)
    cmd2='flirt -in '+tmp_fold+'/FA1.nii.gz -ref '+T1+' -out '+tmp_fold+'/FA2 -omat '+tmp_fold+'/dwi2T1_3D.mat -dof 6 -v'
    print(cmd2)
    os.system(cmd2)
    cmd3='convert_xfm -omat '+tmp_fold+'/dwi2T1.mat -concat '+tmp_fold+'/dwi2T1_3D.mat '+tmp_fold+'/dwi2T1_2D.mat'
    print(cmd3)
    os.system(cmd3)
    cmd4='convert_xfm -omat '+tmp_fold+'/dwi2mni.mat -concat '+tmp_fold+'/T1_acpc.mat '+tmp_fold+'/dwi2T1.mat'
    print(cmd4)
    os.system(cmd4)
    cmd5='flirt -init '+tmp_fold+'/dwi2mni.mat -in '+FA+' -ref '+T1_reg+' -out '+out_dir+'/FA.nii.gz -applyxfm -v'
    print(cmd5)
    os.system(cmd5)
    for im in dti_images[1:]:
        in_im=os.path.join(dti_fold,im)
        out_im=os.path.join(out_dir,im)
        cmd='flirt -init '+tmp_fold+'/dwi2mni.mat -in '+in_im+' -ref '+T1_reg+' -out '+out_im+' -applyxfm -v'
        print(cmd)
        os.system(cmd)
    print('\n\nDTI registration done\n\n')

def loop(dataset_file,template, tmp):
    "Loop for image registration"

    print('\n\nBegin loop for image registration\n\n')
    
    
    script=globals()['acpc_script']
    

    dataset=dataset_file['processed files']['dataset']
    
    output_main_dir=dataset_file['inputs']['reg_dir']
    print('output directory: '+output_main_dir)
    print('\n\nNumber of subject: ',len(dataset.keys()))

    output_dataset=[]
    for subject in dataset.keys():
        print('\n\nStart Subject ',subject)
        T1=dataset[subject]['T1 image']
        dti=dataset[subject]['DTI fold']
        out_dir=os.path.join(output_main_dir,subject)
        if os.path.exists(out_dir):
            os.system('rm -r '+out_dir)
        os.mkdir(out_dir)
        reg_T1_to_mni(T1, template,script,out_dir)
        T1_reg=os.path.join(out_dir, 'T1.nii.gz')
        reg_dti(dti,T1,T1_reg,out_dir)
        dti_reg_fold=out_dir
        output_dataset.append([subject,T1_reg, dti_reg_fold])
        if tmp==False:
            tmp_fold=os.path.join(out_dir, 'tmp')
            cmd='rm -r '+tmp_fold
            print(cmd)
            os.system(cmd)

        print('\n\nSubject: '+subject+' completed\n\n')
    
    print("\n\nAll subject are completed\n\n")
    print("Saving json file\n\n")
    if "Registration" not in dataset_file['inputs']['steps']:
        dataset_file['inputs']['steps'].append("Registration")
    dataset_ditc={}
    for sb, T1, dwi_fold in output_dataset:
        dataset_ditc[sb]={'T1 image': os.path.abspath(T1), 'DTI fold':os.path.abspath(dwi_fold)}
    dataset_file['processed files']={'dataset':dataset_ditc}

    dataset_file['inputs']['registration']=True

    jsonfile=os.path.join(dataset_file['inputs']['output_dir'],'dataset.json')
    write_json(dataset_file,jsonfile)

    cmd='cp '+jsonfile+' '+dataset_file['inputs']['project_file']
    print('\nCoping report json in '+dataset_file['inputs']['project_file'])
    print('\n'+cmd)
    os.system(cmd)


templates=os.path.join(os.environ['DELTA_BIT'],'utils/templates')
templates=sorted([fil for fil in os.listdir(templates)
                  if fil.endswith('.nii.gz')])
acpc_script=os.path.abspath(os.path.expandvars('$DELTA_BIT/utils/ACPCalignment.sh'))

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="With this script you can register your dataset."+
                                    "The minimum requirements dataset json file produced by write_json.py and DWI preprocessing.",

                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-n", "--name", help="Project's name", required=True)
    parser.add_argument("-t", "--template", choices=templates, help="choose a template for registration (for testing pretrained models only MNI152_T1_1mm.nii.gz)", default="MNI152_T1_1mm.nii.gz")
    parser.add_argument("--tmp", action='store_true', help="Insert this flag if you want to keep temporary files")
    


    args = parser.parse_args()


    config = vars(args)

    #getting the project
    name=config['name']
    json_path=get_initialised_project(name)
    print('Json file found in: '+json_path)
    json_object=reading_json(json_path)
    
    #getting template
    template=os.path.join(os.environ['DELTA_BIT'],'utils/templates',config['template'])

    #out directory
    json_object['inputs']['reg_dir']=os.path.join(json_object['inputs']['preprocessing_dir'],'registered')
    out_dir=json_object['inputs']['reg_dir']
    if os.path.exists(out_dir):
        os.system('rm -r '+out_dir)
    os.mkdir(out_dir)

    #temporary files
    tmp=config['tmp']
    if tmp==None:
        tmp=False
   
    #loop for registration
    loop(json_object,template,tmp)


    jsonfile=os.path.join(json_object['inputs']['output_dir'],'dataset.json')
    write_json(json_object,jsonfile)

    cmd='cp '+jsonfile+' '+json_object['inputs']['project_file']
    print('\nCoping report json in '+json_object['inputs']['project_file'])
    print('\n'+cmd)
    os.system(cmd)


    