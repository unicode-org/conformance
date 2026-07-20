#!/bin/bash

# Generates new test data, then executes all tests on that new in the new
# directory.
# Save the results
set -e

# Rotate log files
logrotate -s logrotate.state logrotate.conf

# Start background monitor
(while true; do 
  echo "[$(date +%T)] --- VITALS ---"
  # RAM usage
  echo "Memory: $(free -h | awk 'NR==2{print \$3 \" / \" \$2}')"
  # Disk usage for the current workspace
  echo "Disk: $(df -h . | awk 'NR==2{print \$3 \" used / \" \$4 \" avail (\" \$5 \")\"}')"
  # CPU Load
  echo "CPU Load: $(cut -d' ' -f1-3 /proc/loadavg)"
  echo "------------------------"
  sleep 30
done) &
MONITOR_PID=$!
trap 'kill $MONITOR_PID 2>/dev/null || true' EXIT

##########
# Setup (generate) test data & expected values
##########

# Depending on the OS
case "$(uname -s)" in
    Darwin*)    machine=macos;;
    Linux*)     machine=linux;;
    *)          echo "Unsupported platform: $(uname -s)"; exit 1;;
esac
echo "This machine is: ${machine}"

# Ensure that ICU4C binaries have been downloaded locally
if [ ! -d gh-cache ] || [ -z "$(ls -A gh-cache 2>/dev/null)" ]
then
  bash setup_${machine}.sh
fi

# Enable seting the version of NodeJS
# Install NVM if it is not install in CI

export NVM_DIR=$HOME/.nvm
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

export RUSTUP_TOOLCHAIN=1.87

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
all_test_types=$(python3 -c "import json; d=json.load(open('../$source_file')); print(' '.join(sorted(list(set(t for e in d for t in e.get('run', {}).get('test_type', []))))))")
all_icu_versions=$(python3 -c "import json; d=json.load(open('../$source_file')); print(' '.join(sorted(list(set(e.get('run', {}).get('icu_version') for e in d if e.get('run', {}).get('icu_version'))))))")
python3 testdata_gen.py  --icu_versions $all_icu_versions --test_types $all_test_types
# And copy results to subdirectories.
cp -r icu* ../$TEMP_DIR/testData
popd

# Verify that schema files are valid
pushd schema
python3 check_schemas.py $pwd
# And check generated data against schemas.
python3 check_generated_data.py ../$TEMP_DIR/testData
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

all_execs_json=$(python3 -c "import json; d=json.load(open('$source_file')); print(json.dumps(sorted(list(set(e.get('run', {}).get('exec') for e in d if e.get('run', {}).get('exec'))))))")

if python3 -c "import json, sys; sys.exit(0 if 'dart_native' in json.loads(sys.stdin.read()) else 1)" <<< "$all_execs_json" > /dev/null
then
    pushd executors/dart/
    dart pub get
    dart bin/set_version.dart
    mkdir -p build/bundle/bin
    dart compile exe bin/executor.dart -o build/bundle/bin/executor || echo "WARNING: Failed to compile dart_native"
    popd
fi

if python3 -c "import json, sys; sys.exit(0 if 'dart_web' in json.loads(sys.stdin.read()) else 1)" <<< "$all_execs_json" > /dev/null
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
python3 -c "import json; [print(json.dumps(x)) for x in json.load(open('../$source_file'))]" | while read i; do
    if python3 -c "import json, sys; sys.exit(0 if 'prereq' in json.loads(sys.stdin.read()) else 1)" <<< "$i" > /dev/null
    then
        command=$(python3 -c "import json, sys; val = json.loads(sys.stdin.read()).get('prereq', {}).get('command'); print('null' if val is None else val)" <<< "$i")
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
        eval "$command"
    fi
    icu_version=$(python3 -c "import json, sys; val = json.loads(sys.stdin.read()).get('run', {}).get('icu_version'); print('null' if val is None else val)" <<< "$i")
    exec_command=$(python3 -c "import json, sys; val = json.loads(sys.stdin.read()).get('run', {}).get('exec'); print('null' if val is None else val)" <<< "$i")
    test_type=$(python3 -c "import json, sys; val = json.loads(sys.stdin.read()).get('run', {}).get('test_type'); print('null' if val is None else ' '.join(val))" <<< "$i")
    per_execution=$(python3 -c "import json, sys; val = json.loads(sys.stdin.read()).get('run', {}).get('per_execution'); print('null' if val is None else val)" <<< "$i")
    ignore=$(python3 -c "import json, sys; val = json.loads(sys.stdin.read()).get('run', {}).get('ignore'); print('null' if val is None else val)" <<< "$i")
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
python3 check_test_output.py ../$TEMP_DIR/testOutput
popd

# Verify everything
mkdir -p $TEMP_DIR/testReports
pushd verifier

all_execs=$(python3 -c "import json, sys; print(' '.join(json.loads(sys.stdin.read())))" <<< "$all_execs_json")

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
kill $MONITOR_PID

# Clean up directory
# ... after results are reported
#rm -rf ../$TEMP_DIR
