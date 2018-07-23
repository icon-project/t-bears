#!/usr/bin/env python
import os
from setuptools import setup, find_packages

with open(os.path.join('.', 'VERSION')) as version_file:
    version = version_file.read().strip()

requires = [
    'requests>=2.19.1',
    'jsonrpcserver>=3.5.3',
    'sanic>=0.7.0',
    'plyvel>=1.0.4',
    'secp256k1>=0.13.2',
    'eth-keyfile>=0.5.1',
]


setup_options = {
    'name': 'tbears',
    'version': version,
    'description': '`tbears` for ICON SCORE development',
    'author': 'ICON foundation',
    'author_email': 'foo@icon.foundation',
    'packages': find_packages(exclude=['tests*', 'docs']),
    'package_data': {'tbears': ['VERSION']},
    'include_package_data': True,
    'py_modules': ['tbears'],
    'license': "Apache License 2.0",
    'install_requires': requires,
    'test_suite': 'tests',
    'entry_points': {
        'console_scripts': [
            'tbears=tbears:main'
        ],
    },
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6'
    ]
}

setup(**setup_options)
