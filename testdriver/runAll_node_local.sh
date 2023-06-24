#!/bin/bash
set -e

# Runs collation test on only on node
# Test data and output directories are under ~/DDT_DATA
rm -rf ../DDT_DATA/testOutput
rm -rf ../DDT_DATA/testResults

nvm install 16.19.1
nvm use 16.19.1

python3 testdriver.py --icu_version icu71 --test coll_shift_short number_fmt lang_names --exec node --file_base ../DDT_DATA
