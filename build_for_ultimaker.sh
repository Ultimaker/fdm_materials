#!/bin/bash
#
# SPDX-License-Identifier: LGPL-3.0+
#
# Copyright (C) 2019 Ultimaker B.V.
#

set -eu

ARCH="armhf"

SRC_DIR="$(pwd)"
RELEASE_VERSION="${RELEASE_VERSION:-999.999.999}"
DOCKER_WORK_DIR="/build"
BUILD_DIR_TEMPLATE="_build_${ARCH}"
BUILD_DIR="${BUILD_DIR:-${SRC_DIR}/${BUILD_DIR_TEMPLATE}}"

run_env_check="yes"
run_linters="yes"
run_tests="yes"

# Make sure to pass an empty argument to make_docker, else any arguments passed to build_for_ultimaker is passed to make_docker instead!
. ./make_docker.sh ""

env_check()
{
    run_in_docker "./docker_env/buildenv_check.sh"
}

run_build()
{
    run_in_docker "./build.sh" "${@}"
}

deliver_pkg()
{
    run_in_docker chown -R "$(id -u):$(id -g)" "${DOCKER_WORK_DIR}"

    cp "${BUILD_DIR}/"*".deb" "./"
}

run_tests()
{
    echo "Testing!"
    # These tests should never fail! See .gitlab-ci.yml
    ./run_check_material_profiles_new_with_lxml.sh || echo "Material Profile Check with lxml Failed!"
}

run_linters()
{
    run_shellcheck
}

run_shellcheck()
{
    docker run \
        --rm \
        -v "$(pwd):${DOCKER_WORK_DIR}" \
        -w "${DOCKER_WORK_DIR}" \
        "registry.hub.docker.com/koalaman/shellcheck-alpine:stable" \
        "./run_shellcheck.sh"
}

usage()
{
    echo "Usage: ${0} [OPTIONS]"
    echo "  -c   Skip build environment checks"
    echo "  -h   Print usage"
    echo "  -l   Skip code linting"
    echo "  -t   Skip tests"
}

while getopts ":chlt" options; do
    case "${options}" in
    c)
        run_env_check="no"
        ;;
    h)
        usage
        exit 0
        ;;
    l)
        run_linters="no"
        ;;
    t)
        run_tests="no"
        ;;
    :)
        echo "Option -${OPTARG} requires an argument."
        exit 1
        ;;
    ?)
        echo "Invalid option: -${OPTARG}"
        exit 1
        ;;
    esac
done
shift "$((OPTIND - 1))"

if ! command -V docker; then
    echo "Docker not found, docker-less builds are not supported."
    exit 1
fi

if [ "${run_env_check}" = "yes" ]; then
    env_check
fi

if [ "${run_linters}" = "yes" ]; then
    run_linters
fi

run_build "${@}"

if [ "${run_tests}" = "yes" ]; then
    run_tests
fi

deliver_pkg

exit 0
