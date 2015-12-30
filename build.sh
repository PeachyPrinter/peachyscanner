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

function debian_dependancies() {
  echo ""
  echo "------------------------------------"
  echo "Building Dependent Packages for Debian"
  echo "------------------------------------"
  echo "Installing basics"
  sudo apt-get install python-pip python-dev build-essential 
  echo "Installing numpy dependancies"
  sudo apt-get install gfortran libatlas-base-dev 
  echo "Installing kivy dependancies"
  sudo apt-get install libsmpeg-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev libfreetype6-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
  echo "Installing opencv 3 dependancies"
  sudo apt-get install cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
  sudo apt-get install python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev libdc1394-22
  sudo apt-get install libopencv-dev libpng12-dev libtiff4-dev libxine-dev libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev libv4l-dev libqt4-dev
  sudo apt-get install libfaac-dev libmp3lame-dev libopencore-amrnb-dev libopencore-amrwb-dev libtheora-dev libvorbis-dev libxvidcore-dev x264 v4l-utils unzip
}

function install_opencv3() {
  python -c 'import cv2'
  if [ $? != 0 ]
    then
      mkdir tmp
      pushd .
      cd tmp
      wget https://github.com/Itseez/opencv/archive/3.0.0.zip
      unzip 3.0.0.zip -d opencv
      cd opencv
      cd opencv-3.0.0
      mkdir release
      cd release
      cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D WITH_TBB=ON -D WITH_LIBV4L=ON -D WITH_OPENGL=ON ..
      make -j $(nproc)
      sudo make install
      popd
      rm -rf tmp
    else
      echo "Opencv already installed"
  fi
}

debian_dependancies
install_opencv3


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
if [ $? != 0 ]
then
  cd ..
  exit 777
fi
cp /usr/local/lib/python2.7/dist-packages/cv2.so venv/lib/python2.7/site-packages/
source venv/bin/activate
cat requirements.txt | xargs -n 1 pip install


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
pip install --upgrade src/dist/PeachyScanner*.tar.gz

echo "------------------------------------"
echo "Starting Tests"
echo "------------------------------------"

cd test

python run_all_tests.py

if [ $? == 0 ]
then
  mv ../src/dist/*.tar.gz ..

else
	echo "FAILED TESTS"
    exit 777
fi
