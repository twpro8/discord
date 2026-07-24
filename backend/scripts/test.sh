#!/usr/bin/env bash

set -e
set -x

# Making sure the infrastructure is up
bash scripts/prestart.sh "$@"

coverage run -m pytest tests/
coverage report
coverage html --title "${@-coverage}"
