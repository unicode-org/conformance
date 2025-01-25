#!/bin/bash

# Part of the generateDataAndRun.sh file that 
# runs the verifier.
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

# Generates all new test data
source_file=${1:-'run_config.json'}

# ...

# Verify everything
mkdir -p $TEMP_DIR/testReports
pushd verifier

all_test_types=$(jq '.[].run.test_type' ../$source_file | jq -s '.' | jq 'add' | jq 'unique' | jq -r 'join(" ")')
all_execs=$(jq -r 'join(" ")' <<< $all_execs_json)
python3 verifier.py --file_base ../$TEMP_DIR --exec $all_execs --test_type $all_test_types

popd

