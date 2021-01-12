#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import os
import sys

from setuptools import find_packages
from setuptools import setup
from setuptools.command.install import install


VERSION = '0.0.1'


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')
        tag = tag.lstrip('v')

        if tag != VERSION:
            info = f"Git tag: {tag} does not match the version of this app: {VERSION}"
            sys.exit(info)

setup(
    name='vttes',
    version=VERSION,
    license='BSD',
    description='Python Tools for Roll20 / VTTES / Better20 integrations',
    long_description='Python tools.',
    author='William Gibb',
    author_email='williamgibb@gmail.com',
    url='https://github.com/forgedconcordance/vttestools',
    packages=find_packages(include=('vttes',)),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Other',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    install_requires=[
       'cmd2==1.4.0',
        'tabulate==0.8.7',
    ],
    extras_require={
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
    },
    entry_points={
        'console_scripts': [
            'vttestools= vttes.tools.cli:_main',
        ]
    },
    cmdclass={
        'verify': VerifyVersionCommand,
    },
)
