#!/usr/bin/env bash
rm -rf build dist *.egg-info
python setup.py bdist_wheel
