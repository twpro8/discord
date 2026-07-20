#! /usr/bin/env bash

set -e
set -x

# Let the infrastructure start
python src/prestart.py

# Run migrations
alembic upgrade head
