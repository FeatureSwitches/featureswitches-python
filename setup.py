import os
import sys
import warnings

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

path, script = os.path.split(sys.argv[0])
os.chdir(os.path.abspath(path))

install_requires = []
install_requires.append('requests >= 2.9.1')
install_requires.append('dogpile.cache >= 0.5.7')

# Don't import featureswitches module here, since deps may not be installed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'featureswitches'))
from version import VERSION

# Get simplejson if we don't already have json
if sys.version_info < (3, 0):
    try:
        from util import json
    except ImportError:
        install_requires.append('simplejson')

setup(
    name='featureswitches',
    cmdclass={'build_py': build_py},
    version=VERSION,
    description='Python client for FeatureSwitches.com',
    long_description='Python client for FeatureSwitches.com',
    author='Joel Weirauch',
    author_email='joel@featureswitches.com',
    url='https://featureswitches.com',
    packages=['featureswitches'],
    install_requires=install_requires,
    use_2to3=True,
    include_package_data=True,
    test_suite='tests',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ])
