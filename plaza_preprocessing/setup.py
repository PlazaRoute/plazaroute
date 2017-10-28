#!/usr/bin/env python
# encoding: utf-8
from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()


setup(
    name='plaza_routing',
    version='0.0.1',
    description='Plaza routing service for PlazaRoute',
    long_description=readme,
    author='Jonas Matter, Robin Suter',
    author_email='robin@robinsuter.ch',
    url='https://github.com/PlazaRoute/PlazaRoute',
    license="AGLPv3",
    packages=find_packages(exclude=('tests', 'docs'))
)
