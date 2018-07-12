#!/bin/bash

PYVER=$(python -c 'import sys; print(sys.version_info[0])')
if [[ PYVER -ne 3 ]];then
  echo "The script should be run on python3"
  exit 1
fi

pip3 show sphinx 1>/dev/null

if [ $? != 0 ];then
    pip3 install sphinx==1.7.5
fi
pip3 show sphinx_rtd_theme 1>/dev/null

if [ $? != 0 ];then
    pip3 install sphinx_rtd_theme==0.4.0
fi

sphinx-apidoc -o ./ ../ ../setup.py ../tests/
make html
