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


def main():
    parser = argparse.ArgumentParser(description="With this script you can run the standard pipeline to predict probabilistic tractographies."+
                                    "The minimum requirements dataset json file produced by write_json.py",

                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-n", "--name", help="Project's name", required=True)
    parser.add_argument("--tmp", action='store_true', help="Insert this flag if you want to keep temporary files")
    parser.add_argument("--cortex_area",nargs='+', help="Insert here the cortex area you want to predict\n choose between {}".format(models+['all']), default=['all'])
    

    args = parser.parse_args()


    config = vars(args)

    name=config['name']
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