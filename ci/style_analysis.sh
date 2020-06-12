#!/bin/sh

set -eu

git diff origin/master | pycodestyle --config=pycodestyle.ini --diff

exit 0
