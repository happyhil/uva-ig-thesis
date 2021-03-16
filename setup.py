import os
import glob

try:
    from setuptools import setup, find_packages
except ImportError:
    raise ImportError('Install setup tools')

setup(
    name='UvA IG Thesis',
    version='0.1.0',
    author='Simon Vreugdenhil',
    packages=find_packages(),
    include_package_data=True,
    )
