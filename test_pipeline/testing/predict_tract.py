import keras
import sys
import os
import argparse
import numpy as np
import nibabel as nib

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.environ['DELTA_BIT']))

from utils.json_menaging import reading_json, get_initialised_project
from test_pipeline.preprocessing.write_json import write_json
from utils.data_loader import data_gnerator_test_trac, get_box


def predict_tractography(dataset_file, cortex_area):
    test_gen=data_gnerator_test_trac(dataset_file)
    model=dataset_file['inputs']['models']
    model=os.path.join(os.environ['DELTA_BIT'],'trained_models',model,cortex_area+'.h5')

    output_dir=dataset_file['inputs'][cortex_area]
    output_dataset=[]

    header=test_gen.get_header
    affine=test_gen.get_affine
    subjects=test_gen.subjects
    
    box=dataset_file['inputs']['bounding box file']
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
        pred=pred*test_gen[i][0,:,:,:,0]
        to_save=np.zeros(header(i)[0]['dim'][1:4])
        to_save[x_min:x_max,y_min:y_max,z_min:z_max]=pred
        to_save=nib.Nifti1Image(to_save,affine=affine(i)[0], header=header(i)[0])
        out_file=os.path.join(output_dir,subjects[i]+'.nii.gz')
        output_dataset.append([subjects[i], out_file])
        nib.save(to_save,out_file)
        print('Subject '+subjects[i]+' done\n')

    print("\n\nAll subject are completed\n\n")
    print("Saving json file\n\n")
    if cortex_area+" prediction" not in dataset_file['inputs']['steps']:
        dataset_file['inputs']['steps'].append(cortex_area+" prediction")
    for sb, pred in output_dataset:
        dataset_file['processed files']['dataset'][sb][cortex_area]=pred

    jsonfile=os.path.join(dataset_file['inputs']['output_dir'],'dataset.json')
    write_json(dataset_file,jsonfile)

    cmd='cp '+jsonfile+' '+dataset_file['inputs']['project_file']
    print('\nCoping report json in '+dataset_file['inputs']['project_file'])
    print('\n'+cmd)
    os.system(cmd)
    
    print('Done!')


def predict(dataset_file,models):
    for model in models:
        print('\n\nPredicting '+model+' cortex area projection')
        predict_tractography(dataset_file,model)
        keras.backend.clear_session()
        print('\n\n'+model+' Done!\n')
    print('\n\nAll cortex area projection are complete!\n\n')
    print('Done!')




models=[
    'frontal',
    'occipital',
    'parietal',
    'postcentral',
    'precentral',
    'temporal'

]

def main():
    parser = argparse.ArgumentParser(description="With this script you can predict probabilistic tractographies."+
                                    "The minimum requirements dataset json file produced by write_json.py, DWI preprocessing, registration and make network input.",

                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-n", "--name", help="Project's name", required=True)
    parser.add_argument("--cortex_area",nargs='+', help="Insert here the cortex area you want to predict\n choose between {}".format(models+['all']), default='all')
    #parser.add_argument("--tmp", action='store_true', help="Insert this flag if you want to keep temporary files")

    args = parser.parse_args()


    config = vars(args)

    name=config['name']
    json_object=get_initialised_project(name)
    json_object=reading_json(json_object)

    output_dir=json_object['inputs']['output_dir']
    output_dir=os.path.join(output_dir,'tractography_predictions')
    if os.path.exists(output_dir):
        os.system('rm -r '+output_dir)
    os.mkdir(output_dir)
    m=config['cortex_area']
    if m=='all' or 'all' in m:
        m=models
    print('\nCheck cortex area\n\n')
    for item in m:
        check=item in models
        if not check:
            print('\nERROR WITH cortex area: ',item)
            sys.exit()
    print('\n\nCortex area ', m)
    for mod in m:
        os.mkdir(os.path.join(output_dir,mod))
        json_object['inputs'][mod]=os.path.join(output_dir,mod)
    
    predict(json_object,m)

if __name__=='__main__':
    main()
    