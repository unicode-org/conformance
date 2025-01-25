#!/bin/bash

# If there's a problem, exit with error status
set -e

export ICU_PATH=$1
echo "ICU_PATH: $ICU_PATH";
   
# Load and run ICU4C from github release
# Expects full release path to UBUNTU version
# For CPP executor in Data Driven Testing for conformance

# Standard place to 
export TMP="/tmp/icu/"

# It may exist already - remove old stuff
mkdir -p $TMP
rm -rf $TMP/*

# Get the release and unpack.
cp $ICU_PATH $TMP
ls -ltra

pushd $TMP

tar xvfz *.tgz
rm *.tgz

ls -l icu/usr/local/lib

popd

# Remove old version of executor and rebuild
pushd ../executors/cpp
make clean

export LD_LIBRARY_PATH=/tmp/icu/icu/usr/local/lib:$LD_LIBRARY_PATH
export PATH=/tmp/icu/icu/usr/local/bin:$PATH

make

popd
