import os
import json
import sys

def reading_json(files):
    """
    This function read a json file and return a json object
    

    :files: str or path
        path to the json file to read

    """
    with open(files,'r') as openfiles:
        json_object=json.load(openfiles)
    
    return json_object

def get_initialised_project(name):
    """
    Once your project has been initialised a copy of your dataset.json is saved in delta-BIT directory. This function needs to find and read that file

    name: str
            project's name

    """
    print('\n\nSearching project file\n\n')
    path_file=os.environ['DELTA_BIT']+"/test_pipeline/projects/"+name+".json"
    path_file=os.path.abspath(path_file)
    print('looking at the path: ',path_file)
    if not os.path.exists(path_file):
        print('Project name error')
        sys.exit()
    print('\nProject file found!\n\n')
    return path_file
