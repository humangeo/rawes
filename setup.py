#
#   Copyright [2012] [Dan Noble]
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

from setuptools import setup


setup(name='rawes',
      version='0.2',
      description='rawes elasticsearch driver',
      long_description=open('README.md').read(),
      author='Dan Noble',
      author_email='@dwnoble',
      license='Apache-2.0',
      download_url='https://github.com/humangeo/rawes/tarball/master',
      url='https://github.com/humangeo/rawes',
      classifiers=[
          'License :: OSI Approved :: Apache License 2.0 (Apache-2.0)'
      ],
      packages=[
          'rawes',
          'rawes.thrift_elasticsearch'
      ],
      install_requires=[
          'requests==0.13.9'
      ]
      )
