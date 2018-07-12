#!/bin/bash

sphinx-apidoc -o ./ ../ ../setup.py ../tests/
make html
