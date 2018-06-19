#!/bin/bash
set -e

PYVER=$(python -c 'import sys; print(sys.version_info[0])')
if [[ PYVER -ne 3 ]];then
  echo "The script should be run on python3"
  exit 1
fi

if [[ ("$1" = "test" && "$2" != "--ignore-test") || ("$1" = "build") || ("$1" = "deploy") ]]; then
  pip3 install -r requirements.txt

  VER=$(cat tbears/__init__.py | sed -nE 's/__version__ += +"([0-9\.]+)"/\1/p')
  mkdir -p $VER

  if [[ -z "${ICONSERVICEPATH}" || ("$1" = "deploy") ]]; then
    wget "http://tbears.icon.foundation.s3-website.ap-northeast-2.amazonaws.com/$VER/iconservice-$VER-py3-none-any.whl" -P $VER
    pip install --force-reinstall $VER/iconservice-$VER-py3-none-any.whl
  else
    export PYTHONPATH=$ICONSERVICEPATH:$PYTHONPATH
  fi

  if [[ "$2" != "--ignore-test" ]]; then
    python setup.py test
  fi

  if [ "$1" = "build" ] || [ "$1" = "deploy" ]; then
    pip install wheel
    rm -rf build dist *.egg-info
    python setup.py bdist_wheel

    if [ "$1" = "deploy" ]; then
      cp dist/*$VER*.whl $VER
      wget "http://tbears.icon.foundation.s3-website.ap-northeast-2.amazonaws.com/$VER/CHANGELOG.md" -P $VER
      wget "http://tbears.icon.foundation.s3-website.ap-northeast-2.amazonaws.com/$VER/dapp_guide.md" -P $VER
      wget "http://tbears.icon.foundation.s3-website.ap-northeast-2.amazonaws.com/$VER/tbears_jsonrpc_api_v3.md" -P $VER
      tar -cvzf tbears-$VER.tar.gz $VER/*.whl $VER/*.md
      mv tbears-$VER.tar.gz $VER

      pip install awscli
      export AWS_ACCESS_KEY_ID=AKIAJYKHNVJS4GYQTV2Q
      export AWS_SECRET_ACCESS_KEY=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
      aws s3 cp $VER/tbears-$VER.tar.gz s3://tbears.icon.foundation --acl public-read
      aws s3 cp $VER/CHANGELOG.md s3://tbears.icon.foundation --acl public-read
    fi
  fi

  rm -rf $VER
else
  echo "Usage: build.sh [test|build|deploy]"
  echo "  test: run test"
  echo "  build: run test and build"
  echo "  build --ignore-test: run build"
  echo "  deploy: run test, build and deploy to s3"
  echo "  deploy --ignore-test: run build and deploy to s3"
  exit 1
fi

