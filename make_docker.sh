#!/bin/sh
#
# SPDX-License-Identifier: LGPL-3.0+
#
# Copyright (C) 2019 Ultimaker B.V.
#

set -eu

GIT_HASH="$(git rev-parse HEAD)"

DOCKER_IMAGE_NAME="${1:-fdm-materials_${GIT_HASH}}"

DOCKER_FILE_CHANGES=$(git diff docker_env/Dockerfile)

if ! docker inspect --type=image "${DOCKER_IMAGE_NAME}" > /dev/null || [ -n "${DOCKER_FILE_CHANGES}" ]; then

    docker build --rm -f docker_env/Dockerfile -t "${DOCKER_IMAGE_NAME}" .

    if ! docker run --rm --privileged "${DOCKER_IMAGE_NAME}" "./buildenv_check.sh"; then
        echo "Something is wrong with the build environment, please check your Dockerfile."
        docker image rm "${DOCKER_IMAGE_NAME}"
        exit 1
    fi
fi

DOCKER_WORK_DIR="${WORKDIR:-/build}"
PREFIX="/usr"

run_in_docker()
{
    echo "Running '${*}' in docker."
    docker run \
        --rm \
        --privileged \
        -v "$(pwd):${DOCKER_WORK_DIR}" \
        -e "PREFIX=${PREFIX}" \
        -e "RELEASE_VERSION=${RELEASE_VERSION:-}" \
        -w "${DOCKER_WORK_DIR}" \
        "${DOCKER_IMAGE_NAME}" \
        "${@}"
}
