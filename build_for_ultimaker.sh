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
run_verification="yes"
action="none"

env_check()
{
    run_in_docker "./docker_env/buildenv_check.sh"
}

run_build()
{
    run_in_docker "./build.sh" "${@}"
}

run_verification()
{
    echo "Testing!"
    # These tests should never fail!
    ./run_check_material_profiles.sh || echo "Material Profile Check Failed!"
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
    echo "  -s   Skip code verification"
}

while getopts ":a:chls" options; do
    case "${options}" in
    a)
        action="${OPTARG}"
        ;;
    c)
        run_env_check="no"
        ;;
    h)
        usage
        exit 0
        ;;
    s)
        run_verification="no"
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

case "${action}" in
    shellcheck)
        run_shellcheck
        exit 0
        ;;
    build)
        source ./docker_env/make_docker.sh ""
        run_build
        exit 0
        ;;
    build_docker_cache)
        DOCKER_BUILD_ONLY_CACHE="yes"
        source ./docker_env/make_docker.sh ""
        exit 0
        ;;
    none)
        ;;
    ?)
        echo "Invalid action: -${OPTARG}"
        exit 1
        ;;
esac

# Make sure to pass an empty argument to make_docker, else any arguments passed to build_for_ultimaker is passed to make_docker instead!
source ./docker_env/make_docker.sh ""

if [ "${run_env_check}" = "yes" ]; then
    env_check
fi

run_build "${@}"

if [ "${run_verification}" = "yes" ]; then
    run_verification
fi

exit 0
