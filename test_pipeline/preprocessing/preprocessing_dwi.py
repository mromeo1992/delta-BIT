import os 
import sys
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../"))

from utils.json_managing import reading_json, get_initialised_project
from test_pipeline.preprocessing.write_json import write_json


def preprocessing_dwi(dataset_file,tmp):

    """
    In this function is implemented the FSL pipeline for dwi image correction, in particular eddy current and movement correction are performed by the command eddy_correct. 
    If you want to change dwi preprocessing you can modify this function mantening the output structure.

    dataset_file: json obeject, dir
            json file or dictionary of you dataset

    tmp_fold: bool
        True if you want to keep temporary files
    """
    dataset=dataset_file['input files']['dataset']
    output_dir=dataset_file['inputs']['preprocessing_dir']
    output_dir=os.path.join(output_dir,'dwi_preprocessing')
    if os.path.isdir(output_dir):
        os.system('rm -r '+output_dir)
    os.mkdir(output_dir)
    subjects=dataset.keys()
    print('\n\nPreprocessing DWI routine\n\n')
    print('Number of subjects: ', len(subjects))
    output_dataset=[]

    dti_file_to_keep=[
        'dti_FA.nii.gz',
        'dti_L1.nii.gz',
        'dti_L2.nii.gz',
        'dti_L3.nii.gz',
        'dti_V1.nii.gz',
        'dti_V2.nii.gz',
        'dti_V3.nii.gz'
    ]

    for sub in subjects:
        print('\n\nProcessing subject: '+sub)
        T1=dataset[sub]['T1 image']
        dwi=dataset[sub]['DWI image']
        bvecs=dataset[sub]['bvecs file']
        bvals=dataset[sub]['bvals file']

        sub_out=os.path.join(output_dir, sub)
        if os.path.exists(sub_out):
            os.system('rm -r '+sub_out)
        os.mkdir(sub_out)

        tmp_fold=os.path.join(sub_out,'tmp')
        if os.path.exists(tmp_fold):
            os.system('rm -r '+tmp_fold)
        
        os.mkdir(tmp_fold)

        print('eddy_correct '+dwi+' '+tmp_fold+'/data.nii.gz -spline')
        os.system('eddy_correct '+dwi+' '+tmp_fold+'/data.nii.gz -spline')
        
        print('cp '+bvecs+' '+tmp_fold+'/bvecs')
        os.system('cp '+bvecs+' '+tmp_fold+'/bvecs')
        
        print('cp '+bvals+' '+tmp_fold+'/bvals')
        os.system('cp '+bvals+' '+tmp_fold+'/bvals')

        print('fslroi '+tmp_fold+'/data.nii.gz '+tmp_fold+'/A2P_b0 0 1')
        os.system('fslroi '+tmp_fold+'/data.nii.gz '+tmp_fold+'/A2P_b0 0 1')

        print('bet '+tmp_fold+'/A2P_b0 '+tmp_fold+'/nodif_brain -m')
        os.system('bet '+tmp_fold+'/A2P_b0 '+tmp_fold+'/nodif_brain -m')
        
        print('rm '+tmp_fold+'/A2P_b0.nii.gz')
        os.system('rm '+tmp_fold+'/A2P_b0.nii.gz')
        
        print('rm '+tmp_fold+'/nodif_brain.nii.gz')
        os.system('rm '+tmp_fold+'/nodif_brain.nii.gz')
        
        print('dtifit --data='+tmp_fold+'/data.nii.gz --out='+tmp_fold+'/dti --mask='+tmp_fold+'/nodif_brain_mask.nii.gz --bvecs='+bvecs+' --bvals='+bvals+' --verbose')
        os.system('dtifit --data='+tmp_fold+'/data.nii.gz --out='+tmp_fold+'/dti --mask='+tmp_fold+'/nodif_brain_mask.nii.gz --bvecs='+bvecs+' --bvals='+bvals+' --verbose')
        
        for data in dti_file_to_keep:
           print('cp '+tmp_fold+'/'+data+' '+sub_out+'/'+data.replace('dti_',''))
           os.system('cp '+tmp_fold+'/'+data+' '+sub_out+'/'+data.replace('dti_',''))    
    
        if tmp==False:
            print('rm -r '+tmp_fold)
            os.system('rm -r '+tmp_fold)

        output_dataset.append([sub, T1, sub_out])

        print('Subject '+sub+' done!')

    print("\n\nAll subject are completed\n\n")
    print("Saving json file\n\n")
    if "Preprocessing DWI e DTI fit" not in dataset_file['inputs']['steps']:
        dataset_file['inputs']['steps'].append("Preprocessing DWI e DTI fit")
    dataset_ditc={}
    for sb, T1, dwi_fold in output_dataset:
        dataset_ditc[sb]={'T1 image': os.path.abspath(T1), 'DWI fold':os.path.abspath(dwi_fold)}
    dataset_file['processed files']={'dataset':dataset_ditc}

    jsonfile=os.path.join(dataset_file['inputs']['output_dir'],'dataset.json')
    write_json(dataset_file,jsonfile)

    cmd='cp '+jsonfile+' '+dataset_file['inputs']['project_file']
    print('\nCoping report json in '+dataset_file['inputs']['project_file'])
    print('\n'+cmd)
    os.system(cmd)




    print('\n\nDONE!\n\n')


if __name__=='__main__':
    parser = argparse.ArgumentParser(description="With this script you can preprocess your  dwi files."+
                                    "The minimum requirements dataset json file produced by write_json.py.",

                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-n", "--name", help="Project's name", required=True)
    parser.add_argument("--tmp", action='store_true', help="Insert if you want to keep temporary files")

    args = parser.parse_args()


    config = vars(args)

    name=config['name']
    json_path=get_initialised_project(name)
    print('Json file found in: '+json_path)
    json_object=reading_json(json_path)
    tmp=config['tmp']
    if tmp==None:
        tmp=False
    preprocessing_dwi(json_object,tmp)
