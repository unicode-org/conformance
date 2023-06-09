#!/bin/bash

# Generates new test data, then executes all tests on that new in the new
# directory.
# Save the results
set -e

# Enable seting the version of NodeJS
export NVM_DIR=$HOME/.nvm;
source $NVM_DIR/nvm.sh;

#
# Setup
#

export TEMP_DIR=TEMP_DATA
rm -rf $TEMP_DIR

# Clear out old data, then create new directory and copy test / verify data there
mkdir -p $TEMP_DIR/testData

#
# Setup (generate) test data & expected values
# 

# Generates all new test data
pushd testgen
python3 testdata_gen.py  --icu_versions icu73 icu72 icu71 icu70
# cp *.json ../$TEMP_DIR/testData  # Now uses versions
# And get subdirectories, too.
cp -r icu* ../$TEMP_DIR/testData
popd

#
# Run test data tests through all executors
#
# Compile Rust executor code for ICU4X 1.0
pushd executors/rust/
cargo clean
rustup install 1.61
rustup run 1.61 cargo build --release
popd

# Executes all tests on that new data in the new directory
mkdir -p $TEMP_DIR/testOutput

# Invoke all tests on all platforms
pushd testdriver

#ICU73
nvm install 20.1.0
nvm use 20.1.0
python3 testdriver.py --icu_version icu73 --exec node --test_type coll_shift_short number_fmt lang_names --file_base ../$TEMP_DIR --per_execution 10000
echo $?

#ICU72
nvm install 18.14.2
nvm use 18.14.2
python3 testdriver.py  --icu_version icu72 --exec node --test_type coll_shift_short number_fmt lang_names --file_base ../$TEMP_DIR --per_execution 10000
echo $?

#ICU71
nvm install 16.19.1
nvm use 16.19.1
python3 testdriver.py --icu_version icu71 --exec node --test_type coll_shift_short number_fmt --file_base ../$TEMP_DIR --per_execution 10000
echo $?

# ICU70
nvm install 14.21.3
nvm use 14.21.3
python3 testdriver.py --icu_version icu70 --exec node --test_type coll_shift_short number_fmt --file_base ../$TEMP_DIR --per_execution 10000
echo $?

# ICU4X testing
python3 testdriver.py --icu_version icu72 --exec rust --test_type coll_shift_short number_fmt --file_base ../$TEMP_DIR --per_execution 10000
echo $?

# Done with test execution
popd

#
# Run verifier
#

# Verify everything
mkdir -p $TEMP_DIR/testReports
pushd verifier
python3 verifier.py --file_base ../$TEMP_DIR --exec rust node --test_type coll_shift_short number_fmt lang_names 

#python3 verifier.py --file_base ../$TEMP_DIR --exec cpp--test_type coll_shift_short number_fmt lang_names 
popd

#
# Push testresults and test reports to Cloud Storge
# TODO
echo "End-to-end script finished successfully"

# Clean up directory
# ... after results are reported
#rm -rf ../$TEMP_DIR
