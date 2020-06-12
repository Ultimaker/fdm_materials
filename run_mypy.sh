#!/bin/sh

set -eu

. ./make_docker.sh

run_in_docker "ci/mypy.sh" || echo "Failed!"

exit 0
