import os 
import sys
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../"))

from utils.json_maniging import reading_json, get_initialised_project


def preprocessing_dwi(dataset, output_dir):
    subjects=dataset.keys()
    print('\n\nPreprocessing DWI rutine\n\n')
    print('Number of subjects: ', len(subjects))

    for sub in subjects:
        print('\n\nProcessing subject: '+sub)
        dwi=dataset[sub]['DWI image']
        bvecs=dataset[sub]['bvecs file']
        bvals=dataset[sub]['bvals file']

        sub_out=os.path.join(output_dir, sub)
        if os.path.exists(sub_out):
            os.system('rm -r '+sub_out)
        os.mkdir(sub_out)

        tmp=os.path.join(sub_out,'tmp')
        if os.path.exists(tmp):
            os.system('rm -r '+tmp)
        
        os.mkdir(tmp)

        print('eddy_correct '+dwi+' '+tmp+'/data.nii.gz -trilinear')
        os.system('eddy_correct '+dwi+' '+tmp+'/data.nii.gz -trilinear')
        
        print('cp '+bvecs+' '+sub_out+'/bvecs')
        os.system('cp '+bvecs+' '+sub_out+'/bvecs')
        
        print('cp '+bvals+' '+sub_out+'/bvals')
        os.system('cp '+bvals+' '+sub_out+'/bvals')

        print('fslroi '+tmp+'/data.nii.gz '+tmp+'/A2P_b0 0 1')
        os.system('fslroi '+tmp+'/data.nii.gz '+tmp+'/A2P_b0 0 1')

        print('bet '+tmp+'/A2P_b0 '+tmp+'/nodif_brain -m')
        os.system('bet '+tmp+'/A2P_b0 '+tmp+'/nodif_brain -m')
        
        print('rm '+tmp+'/A2P_b0.nii.gz')
        os.system('rm '+tmp+'/A2P_b0.nii.gz')
        
        print('rm '+tmp+'/nodif_brain.nii.gz')
        os.system('rm '+tmp+'/nodif_brain.nii.gz')
        
        print('dtifit --data='+tmp+'/data.nii.gz --out='+tmp+'/dti --mask='+tmp+'/nodif_brain_mask.nii.gz --bvecs='+bvecs+' --bvals='+bvals+' --verbose')
        os.system('dtifit --data='+tmp+'/data.nii.gz --out='+tmp+'/dti --mask='+tmp+'/nodif_brain_mask.nii.gz --bvecs='+bvecs+' --bvals='+bvals+' --verbose')
        
        print('cp -r '+tmp+'/dti* '+sub_out)
        os.system('cp -r '+tmp+'/dti* '+sub_out)

        print('cp '+tmp+'/data.nii.gz '+sub_out)
        os.system('cp '+tmp+'/data.nii.gz '+sub_out)

        print('cp '+tmp+'/nodif_brain_mask.nii.gz '+sub_out)
        os.system('cp '+tmp+'/nodif_brain_mask.nii.gz '+sub_out)        

        print('rm -r '+tmp)
        os.system('rm -r '+tmp)

        print('Subject '+sub+' done!')

    print('\n\nDONE!\n\n')


if __name__=='__main__':
    parser = argparse.ArgumentParser(description="With this script you can preproces your  dwi files."+
                                    "The minimum requirements dataset json file produced by write_json.py.",

                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-n", "--name", help="Project's name", required=True)

    args = parser.parse_args()


    config = vars(args)

    name=config['name']
    json_path=get_initialised_project(name)
    print('Json file found in: '+json_path)
    json_object=reading_json(json_path)
    dataset=json_object['input files']['dataset']
    output_dir=json_object['inputs']['preprocessing_dir']
    preprocessing_dwi(dataset,output_dir)