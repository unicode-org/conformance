# GENERATES THE DATA without running tests!

export TEMP_DIR=TEMP_DATA

# Clear out old data, then create new directory and copy test / verify data there
mkdir -p $TEMP_DIR/testData

#
# Setup (generate) test data & expected values
# 

# Generates all new test data
pushd testgen
python3 testdata_gen.py  --icu_versions icu73 icu72 icu71 icu70 icu69 icu68 icu67
# And get subdirectories, too.
cp -r icu* ../$TEMP_DIR/testData
popd
