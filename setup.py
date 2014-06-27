import os
import sys
from setuptools import setup, find_packages

required_modules = ['selenium', 'pyyaml']

setup(
    name='harmonious',
    version='0.0.1',
    description='Domain Specific Language for UI Automation',
    author='Andrew Abbott',
    author_email='andrew.abbott@gmail.com',
    url='http://github.com/abbotao/harmonious',
    license='MIT',
    packages=find_packages(),
    install_requires=required_modules,
    entry_points={
        'console_scripts': ['harmonious = harmonious.bin:main'],
        }
)