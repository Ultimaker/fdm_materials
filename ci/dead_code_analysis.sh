#!/bin/sh

set -eu

vulture --min-confidence 100 "scripts"

exit 0
