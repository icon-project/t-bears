#!/usr/bin/env python

from setuptools import setup, find_packages

requires = [
    'iconservice',
    'requests',
    'Flask',
    'Flask-RESTful',
    'jsonrpcserver'
]


setup_options = {
    'name': 'tbears',
    'version': '0.0.1',
    'description': '`tbears` for ICON SCORE development',
    'author': 'ICON foundation',
    'packages': find_packages(exclude=['tests*','docs']),
    'py_modules': ['tbears'],
    'license': "Apache License 2.0",
    'install_requires': requires,
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
