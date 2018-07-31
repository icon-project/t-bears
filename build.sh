#!/bin/bash
set -e

HOST="tbears.icon.foundation"
S3_HOST="http://tbears.icon.foundation.s3-website.ap-northeast-2.amazonaws.com"
PRODUCT="tbears"
DEPS="earlgrey iconcommons"
BRANCH=$(git rev-parse --abbrev-ref HEAD)

function clear_build () {
  rm -rf build dist *.egg-info
}

function install_package()
{
  PKG=$1

  URL="${S3_HOST}/$BRANCH/$PKG"
  VERSION=$(curl "$URL/VERSION")
  FILE="${PKG}-${VERSION}-py3-none-any.whl"
  echo "#### $URL/$FILE"
  pip install --force-reinstall "${URL}/$FILE"
}

PYVER=$(python -c 'import sys; print(sys.version_info[0])')
if [[ PYVER -ne 3 ]];then
  echo "The script should be run on python3"
  exit 1
fi

if [[ "$1" == "clear" ]]; then
  clear_build
  exit 0
fi

if [[ ("$1" = "test" && "$2" != "--ignore-test") || ("$1" = "build") || ("$1" = "deploy") ]]; then
  # pip3 install -r requirements.txt

  for PKG in $DEPS
  do
    install_package $PKG
  done

  if [[ -z "${ICONSERVICEPATH}" || ("$1" = "deploy") ]]; then
    install_package "iconservice"
  else
    if [ "$(pip3 list | grep iconservice)" ]; then
        pip uninstall iconservice -y
    fi
    export PYTHONPATH=${ICONSERVICEPATH}:${PYTHONPATH}
  fi

  if [[ "$2" != "--ignore-test" ]]; then
    # python setup.py test
    python -m unittest
  fi

  if [ "$1" = "build" ] || [ "$1" = "deploy" ]; then
    pip install wheel
    clear_build
    python setup.py bdist_wheel

    if [ "$1" = "deploy" ]; then
      VER=$(cat VERSION)

      if [[ -z "${AWS_ACCESS_KEY_ID}" || -z "${AWS_SECRET_ACCESS_KEY}" ]]; then
        echo "Error: AWS keys should be in your environment"
        rm -rf ${VER}
        exit 1
      fi

      S3_URL="s3://${HOST}/${BRANCH}/${PRODUCT}/"
      echo "$S3_URL"

      pip install awscli
      aws s3 cp VERSION "$S3_URL" --acl public-read
      aws s3 cp dist/*$VER*.whl "$S3_URL" --acl public-read

    fi
  fi

  rm -rf ${VER}
else
  echo "Usage: build.sh [test|build|deploy]"
  echo "  test: run test"
  echo "  clear: clear build and dist files"
  echo "  build: run test and build"
  echo "  build --ignore-test: run build"
  echo "  deploy: run test, build and deploy to s3"
  echo "  deploy --ignore-test: run build and deploy to s3"
  exit 1
fi

