#!/usr/bin/env python

import os
from setuptools import setup

setup(name='rawes',
    version='0.2',
    description='rawes elasticsearch driver',
    author='Dan Noble',
    author_email='@dwnoble',
    url='http://github.com/humangeo/rawes',
    packages=['rawes', 'rawes.thrift_elasticsearch'],
	install_requires=['requests==0.13.9'],
)
