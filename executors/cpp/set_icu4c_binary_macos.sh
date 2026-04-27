#!/bin/bash

# If there's a problem, exit with error status
set -e

export ICU_PATH="$ICU_DIR/$ICU_MACOS_TGZ"
echo "ICU_PATH: $ICU_PATH";

# Load and run ICU4C from github release
# Expects full release path to UBUNTU version
# For CPP executor in Data Driven Testing for conformance

# Standard place to
export TMP="/tmp/icu/"

# It may exist already - remove old stuff
# EDIT: For Mac, don't delete these since they contain compiled code
mkdir -p $TMP
#rm -rf $TMP/*

# Get the release and unpack.
cp $ICU_PATH $TMP
ls -ltra

pushd $TMP

export ICU_BASENAME=$(basename $ICU_PATH .tgz)
echo "ICU_BASENAME = ${ICU_BASENAME}"

export ICU_USR="$TMP/$ICU_BASENAME/usr"

mkdir -p "${ICU_BASENAME}"
tar xfz "${ICU_MACOS_TGZ}" -C "${ICU_BASENAME}"
rm "${ICU_MACOS_TGZ}"

# We need to build ICU4C!
cd "${ICU_BASENAME}/icu/source"
./runConfigureICU MacOSX --prefix="$TMP/$ICU_BASENAME/usr"
make -j8
make install

ls -l "${ICU_USR}/lib"

popd

# Remove old version of executor and rebuild
pushd ../executors/cpp
make clean

export DYLD_LIBRARY_PATH="${ICU_USR}/lib:$LD_LIBRARY_PATH"
export PATH="${ICU_USR}/bin:$PATH"

make

# Some of the scripts require that the libs live in /tmp/icu/icu/usr/local/lib
mkdir -p /tmp/icu/icu/usr/local
cp -R "${ICU_USR}/lib" /tmp/icu/icu/usr/local

popd
