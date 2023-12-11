
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


from setuptools import setup, find_namespace_packages



setup(name='dBIT',
      packages=find_namespace_packages(include=["dBIT","dBIT.*"]),
      version='1.0',
      description='delta-BIT. Framework for probabilistic tractography prediction',
      url='https://github.com/mromeo1992/delta-BIT',
      author='Mattia Romeo',
      author_email='mattia.romeo@community.unipa.it',
      license='..............',
      install_requires=[
            "tensorflow-macos==2.10.0",
            "nibabel",
            "numpy",
            "scipy",
            "matplotlib"
      ],
      entry_points={
          'console_scripts': [
              'd-BIT_initialise=dBIT.test_pipeline.preprocessing.write_json:main',
              'd-BIT_preprocessDWI=dBIT.test_pipeline.preprocessing.preprocessing_dwi:main',
              'd-BIT_regDataset=dBIT.test_pipeline.preprocessing.register_dataset:main',
              'd-BIT_predict_thalamus=dBIT.test_pipeline.testing.predict_thalamus:main',
              'd-BIT_only_thalamus_pred=dBIT.test_pipeline.testing.only_thalamus_prediction:main',
              'd-BIT_make_net_input=dBIT.test_pipeline.testing.make_net_input:main',
              'd-BIT_pred_tract=dBIT.test_pipeline.testing.predict_tract:main',
              'd-BIT_full_test_pipeline=dBIT.test_pipeline.testing.full_prediction:main'
          ],
      },
      keywords=['deep learning', 'image segmentation', 'medical image analysis',
                'medical image segmentation', 'delta-BIT', 'image translation']
      )
