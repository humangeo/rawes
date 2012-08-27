#!/usr/bin/env python

import os
from setuptools import setup

setup(name='rawes',
    version='0.2',
    description='rawes elasticsearch driver',
    author='Dan Noble',
    author_email='@dwnoble',
    url='http://github.com/dwnoble/rawes',
    packages=['rawes'],
	install_requires=['requests==0.13.9'],
)
