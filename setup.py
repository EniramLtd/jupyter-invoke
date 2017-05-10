#!/usr/bin/env python
from setuptools import setup

with open('README.rst') as file:
    long_description = file.read()

setup(
      name='jupyter-invoke',
      version='0.3.0',
      description=('Execute Jupyter notebooks non-internatively '
                   'on a server and obtain output from them'),
      long_description=long_description,
      install_requires=['jupyter'],
      tests_require=['pytest',
                     'pytest-runner',
                     'pandas'],
      author='Jarno Saarimaki',
      author_email='jarno.saarimaki@eniram.fi',
      url='git+https://github.com/EniramLtd/jupyter-invoke.git',
      packages=['jupyter_invoke'],
)
