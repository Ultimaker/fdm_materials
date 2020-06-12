#!/bin/sh

set -eu

. ./make_docker.sh

run_in_docker "ci/style_analysis.sh" || echo "Failed!"

exit 0
