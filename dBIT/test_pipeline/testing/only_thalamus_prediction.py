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

import sys
import os
import argparse


from dBIT.test_pipeline.preprocessing.write_json import write_json
from dBIT.test_pipeline.preprocessing.write_json import outputdir_creation
from dBIT.test_pipeline.preprocessing.register_dataset import reg_T1_to_mni


def registration(dataset_file):
    print('\n\nBegin loop for image registration\n\n')
            
            
    script=globals()['acpc_script']
        
    dataset=dataset_file['input files']['dataset']
    output_main_dir=os.path.join(dataset_file['inputs']['preprocessing_dir'],'registered')
    if os.path.exists(output_main_dir):
        os.system('rm -r '+output_main_dir)
    os.mkdir(output_main_dir)
    dataset_file['inputs']['reg_dir']=output_main_dir
    template=os.path.join(os.environ['DELTA_BIT'],'utils','templates','MNI152_T1_1mm.nii.gz')
    print('output directory: '+output_main_dir)
    print('\n\nNumber of subject: ',len(dataset.keys()))
    output_dataset=[]
    for subject in dataset.keys():
        print('\n\nStart Subject ',subject)
        T1=dataset[subject]['T1 image']
        out_dir=os.path.join(output_main_dir,subject)
        if os.path.exists(out_dir):
            os.system('rm -r '+out_dir)
        os.mkdir(out_dir)
        reg_T1_to_mni(T1, template,script,out_dir)
        T1_reg=os.path.join(out_dir, 'T1.nii.gz')
        output_dataset.append([subject,T1_reg])
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
    for sb, T1 in output_dataset:
        dataset_ditc[sb]={'T1 image': os.path.abspath(T1)}
    dataset_file['processed files']={'dataset':dataset_ditc}

    dataset_file['inputs']['registration']=True

    jsonfile=os.path.join(dataset_file['inputs']['output_dir'],'dataset.json')
    write_json(dataset_file,jsonfile)




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
    for sb, T1 in dataset:
        dataset_ditc[sb]={'T1 image': os.path.abspath(T1)}
    json_ditc['input files']={'dataset':dataset_ditc}

    reg=config['registration']
    if reg:
        for sb, T1 in dataset:
            dataset_ditc[sb]={'T1 image': os.path.abspath(T1)}
        json_ditc['processed files']={'dataset':dataset_ditc}
        
        jsonfile=os.path.join(output_dir,'dataset.json')
        write_json(json_ditc,jsonfile)

    else:
        registration(json_ditc)
        jsonfile=os.path.join(output_dir,'dataset.json')        


    cmd='cp '+jsonfile+' '+config['project_file']
    print('\nCoping report json in '+config['project_file'])
    print('\n'+cmd)
    os.system(cmd)
    
    print('\nDone!')


def check_inputs_path(dataset):
    number=len(dataset)
    print('Nuber of subject: ',number)
    print('\n\nChecking data\n\n')
    print('Subject \t T1 \n')
    for sub, T1 in dataset:
        check1=os.path.exists(T1)
        print(sub+' \t'+str(check1))
        if not check1:
            print('\nInput File Error in subject: file missing in '+sub)
            sys.exit()

def get_file_path(dataset_dir, T1_path):
    print('\n\nget_file_path\n\n')

    os.chdir(dataset_dir)
    sub=sorted([subject for subject in os.listdir(dataset_dir)
                if os.path.isdir(subject)])
    dataset=sorted([fold, os.path.join(fold,T1_path)] for fold in sub)
    check_inputs_path(dataset)
    return dataset




home=os.environ['HOME']
model_dir=os.path.abspath(os.path.join(os.environ['DELTA_BIT'], 'dBIT/trained_models'))
models=sorted([mod for mod in os.listdir(model_dir)
                   if os.path.isdir(os.path.join(model_dir,mod))])
json_out_folder=os.path.abspath(os.path.join(os.environ['DELTA_BIT'],'dBIT/test_pipeline','projects'))

acpc_script=os.path.abspath(os.path.expandvars('$DELTA_BIT/dBIT/utils/ACPCalignment.sh'))


def main():
    parser = argparse.ArgumentParser(description="With this script you can directly predict the binary mask of the thalamus of the left hemisphere."+
                                    "The minimum requirements are T1 images in the standard Dataset Structure (view Testing user manual).",

                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-n", "--name", help="Project's name", required=True)
    parser.add_argument("-m","--models",choices=models, help="Insert here the name of the models you want to use",default='pretrained')
    parser.add_argument("--data_type", help="Insert here the extention of the disired output data: possibility nii, nii.gz, mgz",default='nii.gz')
    parser.add_argument("-dir", "--dataset_directory", help="indicate here your main folder which cointains your dataset", required=True)
    parser.add_argument("--T1_path", help="indicate here the T1 image's relative pathname (starting from the subject's folder)", default='T1.nii.gz')
    parser.add_argument("--registration",action="store_true", help="Inser if you data have already been registered on a standard template")
    parser.add_argument("-o", "--output_dir", help="output_directory",default=home+"/project_name")

    args = parser.parse_args()


    config = vars(args)

    #Input variables
    project_name=config['name']
    T1_path=config['T1_path']

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
    
    dataset=get_file_path(dataset_dir=dataset_dir,T1_path=T1_path)

    config['steps']=["Initialising"]
    write_file(config=config,dataset=dataset)

    print('\n\nThalamus prediction\n\n')

    tal_pred_script=os.path.join(os.environ['DELTA_BIT'],'dBIT','test_pipeline','testing','predict_thalamus.py')
    cmd='python '+tal_pred_script+' -n '+project_name
    print(cmd)

    os.system(cmd)


if __name__=='__main__':
    main()