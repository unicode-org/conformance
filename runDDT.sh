#!/bin/bash

# Executes all tests on small data set
# Save the results

export TEMP_DIR=DDT_DATA

# Executes all tests on that new data in the new directory
rm -rf $TEMP_DIR/testOutput
mkdir -p $TEMP_DIR/testOutput

# Invoke all tests on all platforms
pushd testdriver
nvm install 16.19.1
nvm use 16.19.1
python3 testdriver.py --icu_version icu71 --exec node --test_type coll_shift_short number_fmt lang_names --file_base ../$TEMP_DIR --per_execution 10000
echo $?

python3 testdriver.py --icu_version icu71 --exec rust --test_type coll_shift_short number_fmt lang_names --file_base ../$TEMP_DIR --per_execution 1
echo $?

popd

# Verify everything

rm -rf $TEMP_DIR/testReports
mkdir -p $TEMP_DIR/testReports
pushd verifier
python3 verifier.py --file_base ../$TEMP_DIR --exec rust node python --test_type coll_shift_short number_fmt lang_names 

popd

# Push testresults and test reports to Cloud Storge
# TODO
echo $?

# Clean up directory
# ... after results are reported
#rm -rf ../$TEMP_DIR
