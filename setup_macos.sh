#!/bin/bash

# If there's a problem, exit with error status
set -e

# Ensure Homebrew is installed to handle system dependencies
if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew is required but not installed. Please install it from https://brew.sh/"
    exit 1
fi

# Check if json-c is already installed via Homebrew
if ! brew list json-c >/dev/null 2>&1; then
    brew install json-c
fi

# Download ICU4C binaries if the cache directory doesn't exist
if [[ ! -d gh-cache ]]
then
    mkdir -p gh-cache
fi

# Ensure that the Python `enum` module is installed using a modern, robust check
python3 -c 'import sys
try:
    import enum
    print("The enum module is already installed")
except ImportError:
    print("The enum module is not installed yet")
    sys.exit(1)
' || error_code=$?

if [[ ${error_code:-0} -ne 0 ]]
then
    # On Mac, `enum` is a standard built-in library for Python 3.4+.
    # If this fails, the system Python is likely broken or too old, so we install a fresh python3.
    if ! brew list python3 >/dev/null 2>&1; then
        brew install python3
    fi
fi

# Note: The official ICU GitHub releases do NOT contain pre-compiled macOS binaries.
# URLs have been updated to download the source tarballs (-src.tgz).

function download_71_1() {
  if [[ ! -f icu4c-71_1-src.tgz ]]
  then
    curl -L -O https://github.com/unicode-org/icu/releases/download/release-71-1/icu4c-71_1-src.tgz
  fi
}

function download_72_1() {
  if [[ ! -f icu4c-72_1-src.tgz ]]
  then
    curl -L -O https://github.com/unicode-org/icu/releases/download/release-72-1/icu4c-72_1-src.tgz
  fi
}

function download_73_1() {
  if [[ ! -f icu4c-73_1-src.tgz ]]
  then
    curl -L -O https://github.com/unicode-org/icu/releases/download/release-73-1/icu4c-73_1-src.tgz
  fi
}

function download_74_1() {
  if [[ ! -f icu4c-74_1-src.tgz ]]
  then
    curl -L -O https://github.com/unicode-org/icu/releases/download/release-74-1/icu4c-74_1-src.tgz
  fi
}

function download_74_2() {
  if [[ ! -f icu4c-74_2-src.tgz ]]
  then
    curl -L -O https://github.com/unicode-org/icu/releases/download/release-74-2/icu4c-74_2-src.tgz
  fi
}

function download_75_1() {
  if [[ ! -f icu4c-75_1-src.tgz ]]
  then
    curl -L -O https://github.com/unicode-org/icu/releases/download/release-75-1/icu4c-75_1-src.tgz
  fi
}

function download_76_1() {
  if [[ ! -f icu4c-76_1-src.tgz ]]
  then
    curl -L -O https://github.com/unicode-org/icu/releases/download/release-76-1/icu4c-76_1-src.tgz
  fi
}

function download_77_1() {
  if [[ ! -f icu4c-77_1-src.tgz ]]
  then
    curl -L -O https://github.com/unicode-org/icu/releases/download/release-77-1/icu4c-77_1-src.tgz
  fi
}

pushd gh-cache

download_71_1
download_72_1
download_73_1
download_74_1
download_74_2
download_75_1
download_76_1
download_77_1

popd