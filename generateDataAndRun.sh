#!/bin/bash

# Generates new test data, then executes all tests on that new in the new
# directory.
# Save the results
set -e

# Rotate log files
logrotate -s logrotate.state logrotate.conf

##########
# Setup (generate) test data & expected values
##########

# Ensure that ICU4C binaries have been downloaded locally
if [[ ! -d gh-cache ]]
then
  bash setup.sh
fi

# Enable seting the version of NodeJS
# Install NVM if it is not install in CI

export NVM_DIR=$HOME/.nvm
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

if [[ $CI == "true" ]] && ! [ -x "$(command -v nvm)" ]
then
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
    export NVM_DIR="$HOME/.config/nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
    [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
fi

##########
# Regenerate test data and verify against schema
##########

# Clear old data
export TEMP_DIR=TEMP_DATA
rm -rf $TEMP_DIR

# Clear out old data, then create new directory and copy test / verify data there
mkdir -p $TEMP_DIR/testData


# Generates all new test data
source_file=${1:-'run_config.json'}
pushd testgen
all_icu_versions=$(jq '.[].run.icu_version' ../$source_file | jq -s '.' | jq 'unique' | jq -r 'join(" ")')
python3 testdata_gen.py  --icu_versions $all_icu_versions
# And copy results to subdirectories.
cp -r icu* ../$TEMP_DIR/testData
popd

# Verify that schema files are valid
pushd schema
python3 check_schemas.py --schema_base $pwd
# And check generated data against schemas.
python3 check_generated_data.py --schema_base ../$TEMP_DIR/testData
popd

##########
# Run tests using per-platform executors
##########

#
# Run test data tests through all executors
#
# # Compile Rust executor code for ICU4X 1.0
# if jq -e 'index("rust")' <<< $all_execs_json > /dev/null
# then
#     pushd executors/rust/
#     cargo clean
#     cargo build --release
#     popd
# fi

#
# Run Dart executors in a custom way
#

# TODO(?): Figure out why datasets.py can't support running multiple CLI commands,
# if that is the reason why Dart needs custom handling in this end-to-end script

all_execs_json=$(jq '.[].run.exec' $source_file | jq -s '.' | jq 'unique')

if jq -e 'index("dart_native")' <<< $all_execs_json > /dev/null
then
    pushd executors/dart/
    dart pub get
    dart bin/set_version.dart
    dart build cli --target bin/executor.dart -o build/
    popd
fi

if jq -e 'index("dart_web")' <<< $all_execs_json > /dev/null
then
    pushd executors/dart/
    dart pub get
    dart bin/make_runnable_by_node.dart
    popd
fi

# Executes all tests on that new data in the new directory
mkdir -p $TEMP_DIR/testOutput

#
# Invoke all tests on all platforms
#

# Change to directory of `testdriver` (which will be used to invoke each platform executor)
pushd testdriver

# Invoke all tests
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
    ignore=$(jq -r -c '.run.ignore' <<< $i)
    python3 testdriver.py --icu_version $icu_version --exec $exec_command --test_type $test_type --file_base ../$TEMP_DIR --per_execution $per_execution --ignore $ignore
    echo $?
done

# Done with test execution
popd

##########
# Run verifier
##########

# Verify that test output matches schema.
pushd schema
python3 check_test_output.py --schema_base ../$TEMP_DIR/testOutput
popd

# Verify everything
mkdir -p $TEMP_DIR/testReports
pushd verifier

all_test_types=$(jq '.[].run.test_type' ../$source_file | jq -s '.' | jq 'add' | jq 'unique' | jq -r 'join(" ")')
all_execs=$(jq -r 'join(" ")' <<< $all_execs_json)

# Specifies the arrangement of the columns in the summary dashboard
platform_order='ICU4C ICU4J ICU4X NodeJS Dart_Web Dart_Native'
python3 verifier.py --file_base ../$TEMP_DIR --exec $all_execs --test_type $all_test_types --platform_order $platform_order

popd

##########
# Finish and clean up
##########

#
# Push testresults and test reports to Cloud Storge
# TODO
echo "End-to-end script finished successfully"

# Clean up directory
# ... after results are reported
#rm -rf ../$TEMP_DIR
