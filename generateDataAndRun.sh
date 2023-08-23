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

source_file=${1:-'run_config.json'}


# Generates all new test data
pushd testgen
all_icu_versions=$(jq '.[].run.icu_version' ../$source_file | jq -s '.' | jq 'unique' | jq -r 'join(" ")')
python3 testdata_gen.py  --icu_versions $all_icu_versions
# cp *.json ../$TEMP_DIR/testData  # Now uses versions
# And get subdirectories, too.
cp -r icu* ../$TEMP_DIR/testData
popd

all_execs_json=$(jq '.[].run.exec' $source_file | jq -s '.' | jq 'unique')
#
# Run test data tests through all executors
#
# Compile Rust executor code for ICU4X 1.0
if jq -e 'index("rust")' <<< $all_execs_json > /dev/null
then
    pushd executors/rust/
    cargo clean
    rustup install 1.61
    rustup run 1.61 cargo build --release
    popd
fi

if jq -e 'index("dart_native")' <<< $all_execs_json > /dev/null
then
    pushd executors/dart_native/
    dart pub get
    dart compile exe bin/executor.dart
    popd
fi

if jq -e 'index("dart_web")' <<< $all_execs_json > /dev/null
then
    pushd executors/dart_web/
    dart pub get
    dart run bin/make_runnable_by_node.dart
    popd
fi

# Executes all tests on that new data in the new directory
mkdir -p $TEMP_DIR/testOutput

# Invoke all tests on all platforms
pushd testdriver

# Set to use NVM
source "$HOME/.nvm/nvm.sh"

jq -c '.[]' ../$source_file | while read i; do
    if jq -e 'has("prereq")' <<< $i > /dev/null
    then
        command=$(jq -r -c '.prereq.command' <<< $i)
        eval "$command"
    fi
    icu_version=$(jq -r -c '.run.icu_version' <<< $i)
    exec_command=$(jq -r -c '.run.exec' <<< $i)
    test_type=$(jq -r -c '.run.test_type | join(" ")'  <<< $i)
    per_execution=$(jq -r -c '.run.per_execution' <<< $i)
    python3 testdriver.py --icu_version $icu_version --exec $exec_command --test_type $test_type --file_base ../$TEMP_DIR --per_execution $per_execution
    echo $?
done
# Done with test execution
popd

#
# Run verifier
#

# Verify everything
mkdir -p $TEMP_DIR/testReports
pushd verifier
all_test_types=$(jq '.[].run.test_type' ../$source_file | jq -s '.' | jq 'add' | jq 'unique' | jq -r 'join(" ")')
all_execs=$(jq -r 'join(" ")' <<< $all_execs_json)
python3 verifier.py --file_base ../$TEMP_DIR --exec $all_execs --test_type $all_test_types

popd

#
# Push testresults and test reports to Cloud Storge
# TODO
echo "End-to-end script finished successfully"

# Clean up directory
# ... after results are reported
#rm -rf ../$TEMP_DIR
