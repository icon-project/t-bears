#!/bin/bash

PYVER=$(python -c 'import sys; print(sys.version_info[0])')
if [[ PYVER -ne 3 ]];then
  echo "The script should be run on python3"
  exit 1
fi

if [ -z "$(pip3 list | grep sphinx)" ]; then
    pip3 install sphinx==1.7.5
fi
if [ -z "$(pip3 list | grep sphinx-rtd-theme)" ]; then
    pip3 install sphinx-rtd-theme==0.4.0
fi

sphinx-apidoc -o ./ ../ ../setup.py ../tests/
make html
