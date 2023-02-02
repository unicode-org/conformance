# Generates new test data, then executes all tests on that new in the new
# directory.
# Save the results

export TEMP_DIR=TEMP_DATA
rm -rf $TEMP_DIR

# Clear out old data, then create new directory and copy test / verify data there
mkdir -p $TEMP_DIR/testData

# Generates all new test data
cd testgen
python3 testdata_gen.py
cp *.json ../$TEMP_DIR/testData

# Executes all tests on that new data in the new directory
cd ..
mkdir -p $TEMP_DIR/testResults

# Invoke all tests on all platforms
cd testdriver
python3 testdriver.py --exec node --test_type coll_shift_short number_fmt lang_names --file_base ../$TEMP_DIR --per_execution 10000
echo $?
python3 testdriver.py --exec rust --test_type coll_shift_short number_fmt --file_base ../$TEMP_DIR --per_execution 10000
echo $?

# Verify everything
cd ..
mkdir -p $TEMP_DIR/testReports
cd verifier
python3 verifier.py --file_base ../$TEMP_DIR --exec rust node --test_type coll_shift_short number_fmt lang_names 


# Push testresults and test reports to Cloud Storge
# TODO
echo $?

# Clean up directory
# ... after results are reported
#rm -rf ../$TEMP_DIR
