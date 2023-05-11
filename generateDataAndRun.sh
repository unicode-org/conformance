#!/bin/bash

# Generates new test data, then executes all tests on that new in the new
# directory.
# Save the results
set -e

#
# Setup
#

export TEMP_DIR=TEMP_DATA
rm -rf $TEMP_DIR

# Clear out old data, then create new directory and copy test / verify data there
mkdir -p $TEMP_DIR/testData

# Compile Rust executor code for ICU4X 1.0
pushd executors/rust/
cargo clean
cargo build --release --profile icu4x_1_0
popd

#
# Setup (generate) test data & expected values
# 

# Generates all new test data
cd testgen
python3 testdata_gen.py
cp *.json ../$TEMP_DIR/testData

#
# Run test data tests through all executors
#

# Executes all tests on that new data in the new directory
cd ..
mkdir -p $TEMP_DIR/testResults

# Invoke all tests on all platforms
cd testdriver
python3 testdriver.py --exec node --test_type coll_shift_short number_fmt lang_names --file_base ../$TEMP_DIR --per_execution 10000
echo $?
python3 testdriver.py --exec rust --test_type coll_shift_short number_fmt --file_base ../$TEMP_DIR --per_execution 10000
echo $?
#python3 testdriver.py --exec cpp --test_type coll_shift_short --file_base ../$TEMP_DIR --per_execution 10000
#echo $?

#
# Run verifier
#

# Verify everything
cd ..
mkdir -p $TEMP_DIR/testReports
cd verifier
python3 verifier.py --file_base ../$TEMP_DIR --exec rust node --test_type coll_shift_short number_fmt lang_names 

#python3 verifier.py --file_base ../$TEMP_DIR --exec cpp--test_type coll_shift_short number_fmt lang_names 

#
# Push testresults and test reports to Cloud Storge
# TODO
echo "End-to-end script finished successfully"

# Clean up directory
# ... after results are reported
#rm -rf ../$TEMP_DIR
