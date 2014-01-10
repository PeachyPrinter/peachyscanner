#!/bin/bash

./clean.sh
echo "------------------------------------"
echo "Building PeachyScanner"
echo "------------------------------------"
echo ""
echo "------------------------------------"
echo "Extracting Git Revision Number"
echo "------------------------------------"

function trim() { echo $1; }

if [ -z $GIT_HOME ]; then
  if [ -f "/usr/local/bin/git" ]; then
    export GIT_HOME=/usr/local/bin/git
  elif [ -f "/usr/bin/git" ]; then
    export GIT_HOME=/usr/bin/git
  elif [ -f "/bin/git" ]; then
    export GIT_HOME=/bin/git
  else
    echo "Cant find git."
    exit 1
  fi
fi

export GIT_REV_COUNT_RAW=`$GIT_HOME log --pretty=oneline | wc -l`
export GIT_REV_COUNT=`trim $GIT_REV_COUNT_RAW`
export GIT_REV=`$GIT_HOME rev-parse HEAD`

VERSION=$TAG$GIT_REV_COUNT
echo "Version: $VERSION"
echo "# THIS IS A GENERATED FILE " > version.properties
echo "version='$VERSION'" >> version.properties
echo "revision='$GIT_REV'" >> version.properties
echo "Git Revision Number is $GIT_REV_COUNT"
cp version.properties src/VERSION.py

echo "------------------------------------"
echo "Setting up Virtual Evniroment"
echo "------------------------------------"

cd src
virtualenv venv
source venv/bin/activate
pip install --upgrade 

echo "------------------------------------"
echo "Building"
echo "------------------------------------"

python setup.py sdist
if [ $? != 0 ]
then
  exit 777
fi
cd ..

echo "------------------------------------"
echo "Installing Package"
echo "------------------------------------"
echo `pwd`
pip install --upgrade  src/dist/PeachyScanner*.tar.gz

echo "------------------------------------"
echo "Starting Tests"
echo "------------------------------------"

cd test

python tests.py

if [ $? == 0 ]
then
  mv ../src/dist/*.tar.gz ..

else
	echo "FAILED TESTS"
    exit 777
fi
