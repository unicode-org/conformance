#!/bin/bash

# If there's a problem, exit with error status
set -e

if [[ ! -d gh-cache ]]
then
    mkdir -p gh-cache
    pushd gh-cache
    wget https://github.com/unicode-org/icu/releases/download/release-71-1/icu4c-71_1-Ubuntu20.04-x64.tgz
    wget https://github.com/unicode-org/icu/releases/download/release-72-1/icu4c-72_1-Ubuntu22.04-x64.tgz
    wget https://github.com/unicode-org/icu/releases/download/release-73-1/icu4c-73_1-Ubuntu22.04-x64.tgz
    wget https://github.com/unicode-org/icu/releases/download/release-74-1/icu4c-74_1-Ubuntu22.04-x64.tgz
    popd
fi