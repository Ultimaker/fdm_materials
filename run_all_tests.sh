#!/bin/sh

set -eu

. ./make_docker.sh

git fetch

for test in ci/*.sh ; do
    run_in_docker "${test}" || echo "Failed!"
done

echo "Testing done!"

exit 0
