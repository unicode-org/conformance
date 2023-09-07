#!/bin/bash
set -e

# Short tests to check node and icu4x with small amout of data.

# Enable seting the version of NodeJS
export NVM_DIR=$HOME/.nvm;
source $NVM_DIR/nvm.sh;

# Executes all tests on small data set
# Save the results

export TEMP_DIR=DDT_DATA

# Executes all tests on that new data in the new directory
rm -rf $TEMP_DIR/testOutput
mkdir -p $TEMP_DIR/testOutput

# Invoke all tests on all platforms
pushd testdriver
nvm install 20.1.0
nvm use 20.1.0
python3 testdriver.py --icu_version icu73 --exec node --test_type collation_short number_fmt lang_names likely_subtags --file_base  ../$TEMP_DIR --per_execution 10000 --run_limit 10000
echo $?
popd

pushd executors/rust/
cargo clean
    rustup install 1.61
    rustup run 1.61 cargo build --release
popd

# Try with rust
pushd testdriver
python3 testdriver.py --icu_version icu73 --exec rust --test_type collation_short number_fmt lang_names --file_base ../$TEMP_DIR --per_execution 1000  --run_limit 10000

echo $?


popd

# Verify everything

rm -rf $TEMP_DIR/testReports
mkdir -p $TEMP_DIR/testReports
pushd verifier
python3 verifier.py --file_base ../$TEMP_DIR --exec rust node dart_web python --test_type collation_short number_fmt lang_names likely_subtags 

popd


# Push testresults and test reports to Cloud Storge
# TODO
echo $?

# Clean up directory
# ... after results are reported
#rm -rf ../$TEMP_DIR
