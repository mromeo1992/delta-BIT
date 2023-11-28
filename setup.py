from setuptools import setup, find_namespace_packages

setup(name='delta-BIT',
      packages=find_namespace_packages(include=["test_pipeline.*", "utils.*"]),
      version='1.0',
      description='delta-BIT. Framework for probabilistic tractography prediction',
      url='https://github.com/mromeo1992/delta-BIT',
      author='Mattia Romeo',
      author_email='mattia.romeo@community.unipa.it',
      license='..............',
      install_requires=[
            "tensorflow==2.10.0",
            "nibabel",
            "numpy",
            "scipy",
            "matplotlib"
      ],
      entry_points={
          'console_scripts': [
              'd-BIT_initialise=test_pipeline.preprocessing.write_json:main',
              'd-BIT_preprocessDWI=test_pipeline.preprocessing.preprocessing_dwi:main',
              'd-BIT_regDataset=test_pipeline.preprocessing.register_dataset:main',
              'd-BIT_predict_thalamus=test_pipeline.testing.predict_thalamus:main',
              'd-BIT_only_thalamus_pred=test_pipeline.testing.only_thalamus_prediction:main',
              'd-BIT_make_net_input=test_pipeline.testing.make_net_input:main',
              'd-BIT_pred_tract=test_pipeline.testing.predict_tract:main',
              'd-BIT_full_test_pipeline=test_pipeline.testing.full_prediction:main'
          ],
      },
      keywords=['deep learning', 'image segmentation', 'medical image analysis',
                'medical image segmentation', 'delta-BIT', 'image translation']
      )
