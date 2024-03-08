#!/bin/bash

# If there's a problem, exit with error status
set -e

# install libjson-c-dev if not already installed
dpkg --list | grep libjson-c-dev || error_code=$?
if [[ $error_code -ne 0 ]]
then
    sudo apt-get update
    sudo apt-get install libjson-c-dev
fi

# download ICU4C binaries if they don't exist
if [[ ! -d gh-cache ]]
then
    mkdir -p gh-cache
fi

# ensure that the Python `enum` module is installed
# Github Actions uses Python 3.10 as of Feb 2024
python3 -c 'import pkgutil
if pkgutil.find_loader("enum"):
    print("The enum module is already installed")
else:
    print("The enum module is not installed yet")
    sys.exit(1)
'
error_code=$?
if [[ $error_code -ne 0 ]]
then
    sudo apt-get install python3-enum34
fi


function download_71_1() {
  if [[ ! -f icu4c-71_1-Ubuntu20.04-x64.tgz ]]
  then
    wget https://github.com/unicode-org/icu/releases/download/release-71-1/icu4c-71_1-Ubuntu20.04-x64.tgz
  fi
}


function download_72_1() {
  if [[ ! -f icu4c-72_1-Ubuntu22.04-x64.tgz ]]
  then
    wget https://github.com/unicode-org/icu/releases/download/release-72-1/icu4c-72_1-Ubuntu22.04-x64.tgz
  fi
}


function download_73_1() {
  if [[ ! -f icu4c-73_1-Ubuntu22.04-x64.tgz ]]
  then
    wget https://github.com/unicode-org/icu/releases/download/release-73-1/icu4c-73_1-Ubuntu22.04-x64.tgz
  fi
}


function download_74_1() {
  if [[ ! -f icu4c-74_1-Ubuntu22.04-x64.tgz ]]
  then
    wget https://github.com/unicode-org/icu/releases/download/release-74-1/icu4c-74_1-Ubuntu22.04-x64.tgz
  fi
}


function download_74_2() {
  if [[ ! -f icu4c-74_2-Ubuntu22.04-x64.tgz ]]
  then
    wget https://github.com/unicode-org/icu/releases/download/release-74-2/icu4c-74_2-Ubuntu22.04-x64.tgz
  fi
}


 pushd gh-cache

 download_71_1
 download_72_1
 download_73_1
 download_74_1
 download_74_2

 popd
