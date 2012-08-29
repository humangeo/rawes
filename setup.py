#!/usr/bin/env python

import os
from setuptools import setup

setup(name='rawes',
    version='0.2',
    description='rawes elasticsearch driver',
    long_description=open('README.md').read(),
    author='Dan Noble',
    author_email='@dwnoble',
    download_url='https://github.com/humangeo/rawes/tarball/master',
    license='Apache-2.0',
    classifiers=[
        'License :: OSI Approved :: Apache License 2.0 (Apache-2.0)'
    ],
    url='https://github.com/humangeo/rawes',
    packages=['rawes', 'rawes.thrift_elasticsearch'],
	install_requires=['requests==0.13.9'],
)
