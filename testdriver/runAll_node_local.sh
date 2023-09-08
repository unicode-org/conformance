#!/bin/bash
set -e

# Runs collation test on only on node
# Test data and output directories are under ~/DDT_DATA
rm -rf ../DDT_DATA/testOutput
rm -rf ../DDT_DATA/testResults

source "$HOME/.nvm/nvm.sh"

nvm install 20.1.0
nvm use 20.1.0

python3 testdriver.py --icu_version icu73 --test collation_short number_fmt lang_names likely_subtags --exec node --file_base ../DDT_DATA --run_limit 1000 --per_execution 10000

