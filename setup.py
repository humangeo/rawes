#
#   Copyright 2012 The HumanGeo Group, LLC
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import os

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.md")).read()
CHANGES = open(os.path.join(here, "CHANGES.md")).read()

install_requires = [
    'requests>=0.11.1',
    'thrift==0.8.0',
    'python-dateutil>=1.0'
]

classifiers = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules"
]

setup(name='rawes',
      version='0.3.6',
      description='rawes elasticsearch driver',
      long_description="\n" + README + "\n\n" + CHANGES,
      author='Dan Noble',
      author_email='@dwnoble',
      license='Apache-2.0',
      download_url='https://github.com/humangeo/rawes/tarball/master',
      url='https://github.com/humangeo/rawes',
      include_package_data=True,
      zip_safe=False,
      classifiers=classifiers,
      install_requires=install_requires,
      packages=find_packages()
      )
