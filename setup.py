#!/usr/bin/env python
import os
from setuptools import setup, find_packages

with open('requirements.txt') as requirements:
    requires = list(requirements)

version = os.environ.get('VERSION')
if version is None:
    with open(os.path.join('.', 'VERSION')) as version_file:
        version = version_file.read().strip()

package_data = {'tbears': ['data/mainnet.tar.gz']}

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
    'package_data': package_data,
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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ]
}

setup(**setup_options)
