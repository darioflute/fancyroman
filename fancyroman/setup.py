#!/usr/bin/env python

from distutils.core import setup
import json

with open('fancyroman/version.json') as fp:
    _info = json.load(fp)

config = {
    'name': 'fancyroman',
    'version': _info['version'],
    'description': 'Fancy Roman',
    'long_description': 'Program to make Roman images fancier',
    'author': 'Dario Fadda',
    'author_email': 'darioflute@gmail.com',
    'url': 'https://github.com/darioflute/fancyroman.git',
    'download_url': 'https://github.com/darioflute/fancyroman',
    'python_requires':'>=3.14',
    'license': 'GPLv3+',
    'packages': ['fancyroman'],
    'scripts': ['bin/fancyroman'],
    'include_package_data':True,
    'package_data':{'fifimon':['version.json','icons/*.png','copyright.txt']},
    'classifiers':[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: GPLv3+ License",
            "Operating System :: OS Independent",
            "Intended Audience :: Science/Research", 
            "Development Status :: 4 - Beta",
            "Topic :: Scientific/Engineering :: Visualization",
            ]
}

setup(**config)
