#!/usr/bin/env python
# -*- coding:utf-8 -*-
from setuptools import setup, find_packages

#with open('requirements.txt') as requirements_file:
#    install_requirements = requirements_file.read().splitlines()

setup(
    name='sample-cli',
    version='0.0.1',
    description="sample package",
    author="yagami360",
#    install_requres=install_requirements,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            "sample-cli=module.main:main"
        ]
    }    
)
