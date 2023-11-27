import json
import os
import argparse
import numpy as np
import sys


def write_json(dictionary, out_path):
    """
    This function needs to write json file containing the information of your dataset.

    dictionary: dir
            the ditconary you want to write (in accordance to the standard)
    out_path: str
            path of your output json file
    """

    json_object = json.dumps(dictionary, indent=len(dictionary))
    # Writing json
    with open(out_path, "w") as outfile:
        outfile.write(json_object)



def write_file(config, dataset=None):



    #Input variables
    dataset_dir=os.path.abspath(config['dataset_directory'])
    output_dir=os.path.abspath(config['output_dir'])
    print('\n\nWriting report json in: ',output_dir)
    print('\n\n')
    
    config['dataset_directory']=dataset_dir
    config['Number of subject']=len(dataset)

    json_ditc={
        'inputs' : config
        
        }
    # input dataset

    dataset_ditc={}
    for sb, T1, dwi, bvecs, bvals in dataset:
        dataset_ditc[sb]={'T1 image': os.path.abspath(T1), 'DWI image':os.path.abspath(dwi), 'bvecs file':os.path.abspath(bvecs), 'bvals file':os.path.abspath(bvals)}
    json_ditc['input files']={'dataset':dataset_ditc}

    jsonfile=os.path.join(output_dir,'dataset.json')
    write_json(json_ditc,jsonfile)    

    '''json_object = json.dumps(json_ditc, indent=len(config))
    # Writing json
    
    with open(jsonfile, "w") as outfile:
        outfile.write(json_object)'''

    cmd='cp '+jsonfile+' '+config['project_file']
    print('\nCoping report json in '+config['project_file'])
    print('\n'+cmd)
    os.system(cmd)
    
    print('\nDone!')

def check_inputs_path(dataset):
    number=len(dataset)
    print('Nuber of subject: ',number)
    print('\n\nChecking data\n\n')
    print('Subject \t T1 \tDWI \tbvecs \tbvals \n')
    for sub, T1, dwi, bvecs, bvals in dataset:
        check1=os.path.exists(T1)
        check2=os.path.exists(dwi)
        check3=os.path.exists(bvecs)
        check4=os.path.exists(bvals)
        print(sub+' \t'+str(check1)+' \t'+str(check2)+' \t'+str(check3)+' \t'+str(check4))
        if not check1*check2*check3*check4:
            print('\nInput File Error in subject: file missing in '+sub)
            sys.exit()

def get_file_path(dataset_dir, T1_path, dwi_path, bvecs, bvals):
    print('\n\nget_file_path\n\n')

    os.chdir(dataset_dir)
    sub=sorted([subject for subject in os.listdir(dataset_dir)
                if os.path.isdir(subject)])
    dataset=sorted([fold, os.path.join(fold,T1_path),os.path.join(fold,dwi_path),os.path.join(fold,bvecs),os.path.join(fold,bvals)] for fold in sub)
    check_inputs_path(dataset)
    return dataset


def outputdir_creation(output_dir):

    
    print('\nChecking output directory: ',output_dir)
    if not os.path.exists(output_dir):
        print("\nCreating output directory: "+output_dir)
        os.mkdir(output_dir)
        preprocessing_dir=os.path.join(output_dir,'preprocessing')
        os.mkdir(preprocessing_dir)
        globals()['preprocessing_dir']=preprocessing_dir
        globals()['output_dir']=output_dir

    else:
        print('\noutput directory already exists!')
        test=0
        while test==0:
            decision=str(input('Do you want to overwrite? yes/no: '))    
            if decision=='yes':
                print('Removing old folder')
                os.system('rm -r '+output_dir)
                print("Creating output directory: "+output_dir)
                os.mkdir(output_dir)
                preprocessing_dir=os.path.join(output_dir,'preprocessing')
                os.mkdir(preprocessing_dir)
                globals()['preprocessing_dir']=preprocessing_dir
                globals()['output_dir']=output_dir
                test=1
            elif decision=='no':
                sys.exit()
            else:
                print('input error: choose yes or no')






home=os.environ['HOME']
model_dir=os.path.abspath(os.path.join(os.environ['DELTA_BIT'], 'trained_models'))
models=sorted([mod for mod in os.listdir(model_dir)
                   if os.path.isdir(os.path.join(model_dir,mod))])
json_out_folder=os.path.abspath(os.path.join(os.environ['DELTA_BIT'],'test_pipeline','projects'))

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="With this script you can create the dataset json file for your own dataset."+
                                    "The minimum requirements are T1 images and DWI data placed in the standard Dataset Structure (view Preporcessing user manual).",

                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-n", "--name", help="Project's name", required=True)
    parser.add_argument("-m","--models",choices=models, help="Insert here the name of the models you want to use",default='pretrained')
    parser.add_argument("--data_type", help="Insert here the extention of the disired output data: possibility nii, nii.gz, mgz",default='nii.gz')
    parser.add_argument("-dir", "--dataset_directory", help="indicate here your main folder which cointains your dataset", required=True)
    parser.add_argument("--T1_path", help="indicate here the T1 image's relative pathname (starting from the subject's folder)", default='T1.nii.gz')    
    parser.add_argument("--dwi_path", help="indicate here the DWI image's relative pathname (starting from the subject's folder)", default='DWI.nii.gz')
    parser.add_argument("--bvecs", help="indicate here the bvecs's relative pathname (starting from the subject's folder)", default='DWI.bvec')
    parser.add_argument("--bvals", help="indicate here the bvals's relative pathname (starting from the subject's folder)", default='DWI.bval')
    parser.add_argument("--registration",action="store_true", help="Inser if you data have already been registered on a standard template")
    parser.add_argument("-o", "--output_dir", help="output_directory",default=home+"/project_name")

    args = parser.parse_args()


    config = vars(args)

    #Input variables
    project_name=config['name']
    T1_path=config['T1_path']
    dwi_path=config['dwi_path']
    bvecs=config['bvecs']
    bvals=config['bvals']
    dataset_dir=os.path.abspath(config['dataset_directory'])
    #print(dataset_dir)
    output_dir=os.path.abspath(config['output_dir'])
    if output_dir==home+"/project_name":
        output_dir=os.path.join(home, project_name)

    if not config['registration']:
        config['registration']=False

    project_file=os.path.join(json_out_folder,project_name+'.json')
    config['project_file']=project_file
    outputdir_creation(output_dir)
    config['output_dir']=output_dir
    config['preprocessing_dir']=os.path.join(output_dir,'preprocessing')

    data_type='.'+config['data_type']
    
    dataset=get_file_path(dataset_dir=dataset_dir,T1_path=T1_path,dwi_path=dwi_path, bvecs=bvecs, bvals=bvals)

    config['steps']=["Initialising"]
    write_file(config=config,dataset=dataset)

