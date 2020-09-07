#!/bin/sh

ARCH="armhf"

# Common directory variables
SYSCONFDIR="${SYSCONFDIR:-/etc}"
SRC_DIR="$(pwd)"
BUILD_DIR_TEMPLATE="_build_${ARCH}"
BUILD_DIR="${BUILD_DIR:-${SRC_DIR}/${BUILD_DIR_TEMPLATE}}"

# Debian package information
PACKAGE_NAME="${PACKAGE_NAME:-fdm-materials}"
RELEASE_VERSION="${RELEASE_VERSION:-999.999.999}"

build()
{
    mkdir -p "${BUILD_DIR}"
    cd "${BUILD_DIR}" || return
    echo "Building with cmake"
    cmake .. -DCMAKE_INSTALL_PREFIX=/usr -DCPACK_PACKAGE_VERSION="${RELEASE_VERSION}" -DCPACK_PACKAGE_NAME="${PACKAGE_NAME}" -DCPACK_PACKAGE_ARCH="${ARCH}" -DEMBEDDED=ON
}

create_debian_package()
{
    make package
}

cleanup()
{
    rm -rf "${BUILD_DIR:?}"
}

usage()
{
    echo "Usage: ${0} [OPTIONS]"
    echo "  -c   Explicitly cleanup the build directory"
    echo "  -h   Print this usage"
    echo "NOTE: This script requires root permissions to run."
}

while getopts ":hc" options; do
    case "${options}" in
    c)
        cleanup
        exit 0
        ;;
    h)
        usage
        exit 0
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

cleanup
build
create_debian_package
