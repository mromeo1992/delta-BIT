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
    path_file=os.environ['DELTA_BIT']+"/dBIT/test_pipeline/projects/"+name+".json"
    path_file=os.path.abspath(path_file)
    print('looking at the path: ',path_file)
    if not os.path.exists(path_file):
        print('Project name error')
        sys.exit()
    print('\nProject file found!\n\n')
    return path_file
