#!/usr/bin/env python
import os
from setuptools import setup, find_packages

version = os.environ.get('VERSION')

if version is None:
	with open(os.path.join('.', 'VERSION')) as version_file:
		version = version_file.read().strip()

requires = [
    'earlgrey',
    'iconcommons',
    'iconrpcserver>=1.0.3',
    'iconservice>=1.0.3',
    'requests>=2.19.1',
    'plyvel>=1.0.4',
    'secp256k1>=0.13.2',
    'eth-keyfile>=0.5.1',
    'ipython>=6.4.0',
]


setup_options = {
    'name': 'tbears',
    'version': version,
    'description': 'Test suite for ICON SCORE development',
    'long_description': open('README.md').read(),
    'long_description_content_type': "text/markdown",
    'url': 'https://github.com/icon-project/t-bears',
    'author': 'ICON Foundation',
    'author_email': 'foo@icon.foundation',
    'packages': find_packages(exclude=['tests*', 'docs']),
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
        'Programming Language :: Python :: 3.6'
    ]
}

setup(**setup_options)
