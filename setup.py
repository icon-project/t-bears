#!/usr/bin/env python

from setuptools import setup, find_packages
from tbears import __version__


requires = [
    'requests==2.18.4',
    'jsonrpcserver==3.5.4',
    'aio_pika == 2.8.1',
    'sanic == 0.7.0'
]


setup_options = {
    'name': 'tbears',
    'version': __version__,
    'description': '`tbears` for ICON SCORE development',
    'author': 'ICON foundation',
    'author_email': 'foo@icon.foundation',
    'packages': find_packages(exclude=['tests*','docs']),
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
