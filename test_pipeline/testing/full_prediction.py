import sys
import os
import argparse


models=[
    'frontal',
    'occipital',
    'parietal',
    'postcentral',
    'precentral',
    'temporal'

]

home=os.environ['HOME']
model_dir=os.path.abspath(os.path.join(os.environ['DELTA_BIT'], 'trained_models'))
models=sorted([mod for mod in os.listdir(model_dir)
                   if os.path.isdir(os.path.join(model_dir,mod))])
json_out_folder=os.path.abspath(os.path.join(os.environ['DELTA_BIT'],'test_pipeline','projects'))


def main():
    parser = argparse.ArgumentParser(description="With this script you can run the standard pipeline to predict probabilistic tractographies."+
                                    "The minimum requirement is the dataset preparation in accordance with the dataset structure",

                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-n", "--name", help="Project's name", required=True)
    parser.add_argument("-m","--models",choices=models, help="Insert here the name of the models you want to use",default='pretrained')
    parser.add_argument("--data_type", help="Insert here the extention of the disired output data: possibility nii, nii.gz, mgz",default='nii.gz')
    parser.add_argument("-dir", "--dataset_directory", help="indicate here your main folder which cointains your dataset", required=True)
    parser.add_argument("--T1_path", help="file name of the T1 image", default='T1.nii.gz')    
    parser.add_argument("--dwi_path", help="file name of the DWI image", default='DWI.nii.gz')
    parser.add_argument("--bvecs", help="file name of the bvecs file", default='DWI.bvec')
    parser.add_argument("--bvals", help="file name of the bvals file", default='DWI.bval')
    parser.add_argument("--registration",action="store_true", help="Inser if you data have already been registered on a standard template")    
    parser.add_argument("--tmp", action='store_true', help="Insert this flag if you want to keep temporary files")
    parser.add_argument("--cortex_area",nargs='+', help="Insert here the cortex area you want to predict\n choose between {}".format(models+['all']), default=['all'])
    parser.add_argument("-o", "--output_dir", help="output_directory",default=home+"/project_name")
    

    args = parser.parse_args()


    config = vars(args)

    name=config['name']
    model=config['models']
    datatype=config['data_type']
    directory=config['dataset_directory']ù
    T1=config['T1_path']
    dwi=config['dwi_path']
    bvecs=config['bvecs']
    bvals=config['bvals']
    reg=config['registration']
    if reg==None:
        reg=False
    outfold=config['output_dir']
    cortex_area=config['cortex_area']


    print('\nYou select the subsequent areas: \n')
    print(cortex_area)
    print('\n')
    test=0
    while test==0:
        decision=str(input('Is it correct? yes/no: '))    
        if decision=='yes':
            print('\nStarting test pipeline')
            test=1
        elif decision=='no':
            print('Exit')
            sys.exit()
        else:
            print('input error: choose yes or no')


    tmp=config['tmp']
    if tmp==None:
        tmp=False

    #initialise project
    cmd='d-BIT_initialise -n '+name+' -m '+model+' --data_type '+datatype+' -dir '+directory+' --T1_path '+T1+' --dwi_path '+dwi+'  --bvecs '+bvecs+' --bvals '+bvals
    if reg:
        cmd=cmd+' --registration'
    
    cmd=cmd+' -o '+outfold
    print('\nRunning: '+cmd)
    os.system(cmd)

    #Preprocessing DWI
    cmd='d-BIT_preprocessDWI -n '+name
    if tmp:
        cmd=cmd+' --tmp'
    print('Running: '+cmd)
    os.system(cmd)

    #Register dataset
    cmd='d-BIT_regDataset -n '+name
    if tmp:
        cmd=cmd+' --tmp'
    print('Running: '+cmd)
    os.system(cmd)

    #Predict thalamus
    cmd='d-BIT_predict_thalamus -n '+name
    print('Running: '+cmd)
    os.system(cmd)

    #Make network inputs
    cmd='d-BIT_make_net_input -n '+name
    print('Running: '+cmd)
    os.system(cmd)

    #Predict tractographies
    cmd='d-BIT_pred_tract -n '+name+' --cortex_area'
    for m in cortex_area:
        cmd=cmd+' '+m
    print('Running: '+cmd)
    os.system(cmd)


    



if __name__=='__main__':
    main()