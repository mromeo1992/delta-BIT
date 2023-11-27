import keras
import sys
import os
import argparse
import numpy as np
import nibabel as nib

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.environ['DELTA_BIT']))

from utils.json_menaging import reading_json, get_initialised_project
from test_pipeline.preprocessing.write_json import write_json
from utils.data_loader import data_generator_test_T1, get_box

def predict_thalamus(dataset_file):

    box=dataset_file['inputs']['bounding box file']

    test_gen=data_generator_test_T1(dataset_file,box_path=box)
    model=os.path.join(os.environ['DELTA_BIT'],'trained_models', dataset_file['inputs']['models'], 'thalamus.h5')
    output_dir=dataset_file['inputs']['thalamus predictions']
    output_dataset=[]

    header=test_gen.get_header
    affine=test_gen.get_affine
    subjects=test_gen.subjects
    

    box=get_box(box)
    x_min, x_max = box['x_min'], box['x_max']
    y_min, y_max = box['y_min'], box['y_max']
    z_min, z_max = box['z_min'], box['z_max']
    img_size=(x_max-x_min,y_max-y_min,z_max-z_min)

    print('\n\nPredicting dataset\n\n')
    model=keras.models.load_model(model, compile=False)
    predictions=model.predict(test_gen)

    print('\n\nSaving predictions in: '+output_dir+'\n\n')
    for i in range(len(predictions)):
        pred=predictions[i].reshape(img_size)
        pred=pred > 0.5
        pred=pred.astype('uint16')
        to_save=np.zeros(header(i)[0]['dim'][1:4])
        to_save[x_min:x_max,y_min:y_max,z_min:z_max]=pred
        to_save=nib.Nifti1Image(to_save,affine=affine(i)[0],header=header(i)[0])
        out_file=os.path.join(output_dir,subjects[i]+'.nii.gz')
        output_dataset.append([subjects[i], out_file])
        nib.save(to_save,out_file)
        print('Subject '+subjects[i]+' done\n')

    print("\n\nAll subject are completed\n\n")
    print("Saving json file\n\n")
    if "Thalamus prediction" not in dataset_file['inputs']['steps']:
        dataset_file['inputs']['steps'].append("Thalamus prediction")
    for sb, tal in output_dataset:
        dataset_file['processed files']['dataset'][sb]['Thalamus']=tal

    jsonfile=os.path.join(dataset_file['inputs']['output_dir'],'dataset.json')
    write_json(dataset_file,jsonfile)

    cmd='cp '+jsonfile+' '+dataset_file['inputs']['project_file']
    print('\nCoping report json in '+dataset_file['inputs']['project_file'])
    print('\n'+cmd)
    os.system(cmd)
    
    print('Done!')

    




if __name__=='__main__':
    parser = argparse.ArgumentParser(description="With this script you can predict thalamus mask."+
                                    "The minimum requirements dataset json file produced by write_json.py, DWI preprocessing and registration.",

                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-n", "--name", help="Project's name", required=True)
    parser.add_argument("--box",help="If you want to use another bounding box insert here the path of the file", default="default")
    #parser.add_argument("--tmp", action='store_true', help="Insert this flag if you want to keep temporary files")

    args = parser.parse_args()


    config = vars(args)

    name=config['name']
    json_object=get_initialised_project(name)
    json_object=reading_json(json_object)

    output_dir=json_object['inputs']['output_dir']
    output_dir=os.path.join(output_dir,'thalamus_prediction')
    if os.path.exists(output_dir):
        os.system('rm -r '+output_dir)
    os.mkdir(output_dir)
    
    box=config['box']
    if box=="default":
        box=os.path.join(os.environ['DELTA_BIT'],'utils/cropping_border_default.npz')
    
    json_object['inputs']['bounding box file']=box
    json_object['inputs']['thalamus predictions']=output_dir

    predict_thalamus(json_object)