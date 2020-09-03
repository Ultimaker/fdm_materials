#!/bin/sh

set -eu

CROSS_COMPILE="${CROSS_COMPILE:-""}"

COMMANDS=" \
cmake \
make \
python3 \
pip3 \
git \
"
result=0

echo_line(){
    echo "--------------------------------------------------------------------------------"
}

check_command_installation()
{
    for pkg in ${COMMANDS}; do
        PATH="${PATH}:/sbin:/usr/sbin:/usr/local/sbin" command -V "${pkg}" || result=1
    done
}

echo_line
echo "Verifying build environment commands:"
check_command_installation
echo_line

if [ "${result}" -ne 0 ]; then
    echo "ERROR: Missing preconditions, cannot continue."
    exit 1
fi

echo_line
echo "Build environment OK"
echo_line

exit 0
