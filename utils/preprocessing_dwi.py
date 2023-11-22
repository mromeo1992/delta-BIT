import os
import numpy as np
import nibabel as nib
#eddy_correct senza upsampling


#per funzionare è necessario fornire la cartella data_orig all'interno di ogni soggetto (cartelle che terminano con _NII)
#contenente i file .nii.gz delle immagini T1 e DWI e dei fale ASCII aventi estensione .bevec .bvals

#scansione soggetti
cwd='./'
lista=os.listdir(cwd)
lista_soggetti=[]
for dato in lista:
    if dato.endswith('_NII'):
        lista_soggetti.append(dato)
lista_soggetti.sort()
print(lista_soggetti)
print('Numero soggetti: ', len(lista_soggetti))

dwi_filename='DATA.nii.gz'  #nome dato pesato in diffusione accertarsi che durante la conversione dal formato dicom venga dato questo nome




for soggetto in lista_soggetti:
    cwd_sogg=cwd+soggetto+'/'
    output_folder='data_util'
    if output_folder in os.listdir(cwd_sogg):
        os.system('rm -r '+cwd_sogg+output_folder)
    os.mkdir(cwd_sogg+output_folder)
    output_folder=cwd_sogg+output_folder+'/'
    data_orig_folder=cwd_sogg+'data_orig/'
    os.system('eddy_correct '+data_orig_folder+dwi_filename+' '+output_folder+'data.nii.gz -trilinear')
    os.system('cp '+cwd_sogg+'data_orig/DATA.bvec '+output_folder+'bvecs')
    os.system('cp '+cwd_sogg+'data_orig/DATA.bval '+output_folder+'bvals')
    os.system('fslroi '+output_folder+'data.nii.gz '+output_folder+'A2P_b0 0 1')
    os.system('bet '+output_folder+'A2P_b0 '+output_folder+'nodif_brain -m')
    os.system('rm '+output_folder+'A2P_b0.nii.gz')
    os.system('rm '+output_folder+'nodif_brain.nii.gz')
    if 'data_dti' not in os.listdir(cwd_sogg):
        os.mkdir(cwd_sogg+'data_dti')
    cwd_data_dti=cwd_sogg+'data_dti/'
    os.system('dtifit --data='+output_folder+'data.nii.gz --out='+cwd_data_dti+'/data --mask='+output_folder+'/nodif_brain_mask.nii --bvecs='+output_folder+'bvecs --bvals='+output_folder+'bvals --verbose')
    os.system('cp '+cwd_data_dti+'data_FA.nii.gz '+output_folder+'data_DMC_L0_FA.nii.gz')
