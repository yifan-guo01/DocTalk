import subprocess
from sys import platform
import os
from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()
with open("README.md","r") as f:
    long_description = f.read()

version = "0.3.4"
setup(name='doctalk',
  version=version,
  description='doctalk: Dialogue agent handling queries about a given text document',
  long_description = long_description,
  long_description_content_type='text/markdown',
  url='https://github.com/ptarau/pytalk.git',
  author='Paul Tarau',
  author_USER_EMAIL='<paul.tarau@gmail.com>',
  license='Apache',
  packages=['doctalk'],
  package_data={'doctalk': ['*json','*.txt']},
  include_package_data=True,
  install_requires = required,
  zip_safe=False
  )

