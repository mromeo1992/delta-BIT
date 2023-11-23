import keras
import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../"))

from utils.json_menaging import reading_json, get_initialised_project
from test_pipeline.preprocessing.write_json import write_json
from utils.data_loader import data_generator_test_T1

def predict_thalamus(dataset_file, output_dir, model):
    test_gen=data_generator_test_T1(dataset_file)
    model=keras.models.load_model(model, compile=False)
    predictions=model.predict(test_gen)

    




if __name__=='__main__':
    parser = argparse.ArgumentParser(description="With this script you can predict thalamus mask."+
                                    "The minimum requirements dataset json file produced by write_json.py, DWI preprocessing and registration.",

                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-n", "--name", help="Project's name", required=True)
    #parser.add_argument("--tmp", action='store_true', help="Insert this flag if you want to keep temporary files")

    args = parser.parse_args()


    config = vars(args)

    name=config['name']
    json_object=get_initialised_project(name)
    json_object=reading_json(json_object)

    model=os.path.join(os.environ['DELTA_BIT'], json_object['inputs'], 'thalamus.h5')

    output_dir=json_object['inputs']['output_dir']
    output_dir=os.path.join(output_dir,'thalamus_prediction')
    if os.path.exists(output_dir):
        os.system('rm -r '+output_dir)
    os.mkdir(output_dir)