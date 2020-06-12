#!/bin/sh

set -eu

. ./make_docker.sh

run_in_docker python3 scripts/check_material_profiles_new_with_lxml.py || echo "Failed!"

exit 0