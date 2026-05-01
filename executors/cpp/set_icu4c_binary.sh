#!/bin/bash

# If there's a problem, exit with error status
set -e

export ICU_DIR=$1
export ICU_LINUX_TGZ=$2
export ICU_MACOS_TGZ=$3

# Depending on the OS
case "$(uname -s)" in
    Darwin*)    machine=macos;;
    Linux*)     machine=linux;;
    *)          machine="UNKNOWN";;
esac
echo "This machine is: ${machine}"

# Get the directory where THIS script is stored
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

# Ensure that ICU4C binaries have been downloaded locally
if [[ ! -d gh-cache ]]
then
  bash "$SCRIPT_DIR/set_icu4c_binary_${machine}.sh"
fi
