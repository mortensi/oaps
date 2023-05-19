from setuptools import find_packages, setup

setup(
    name='oaps',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'sentence_transformers',
        'img2vec_pytorch',
        'shortuuid',
        'pandas',
        'redis'
    ],
)
