#!/usr/bin/env python

from distutils.core import setup

setup(name='rawes',
    version='0.1',
    description='RawES elasticsearch driver',
    author='Dan Noble',
    author_email='@dwnoble',
    url='http://github.com/dwnoble/rawes',
    packages=['distutils', 'distutils.command', 'thrift (>=0.8.0)'],
)
