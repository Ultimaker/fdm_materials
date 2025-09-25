FROM --platform=linux/amd64 registry.hub.docker.com/library/debian:bookworm

# Set up a Python virtual environment.
# This isolates project dependencies from the system's Python.
# We include --system-site-packages to allow access to apt-installed modules
# like dbus or gi, which are often system-level dependencies.
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

LABEL Maintainer="software-embedded-platform@ultimaker.com" \
      Comment="Ultimaker update-tools filesystem"

RUN apt-get update && apt-get -y install cmake make python3 python3-pip python3-venv git libxml2-dev libxslt-dev

# Create the Python virtual environment.
RUN python3 -m venv --system-site-packages ${VIRTUAL_ENV}

COPY docker_env/buildenv_check.sh buildenv_check.sh

COPY fdm_requirements.txt fdm_requirements.txt

RUN pip3 install -r fdm_requirements.txt
