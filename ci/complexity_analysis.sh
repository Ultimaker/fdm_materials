#!/bin/sh

set -eu

# Shouldn't expect 100% success rate
lizard -Eduplicate scripts -T cyclomatic_complexity=20 #This value shall not increase, target is <= 10

exit 0
