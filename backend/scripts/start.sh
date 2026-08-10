#! /usr/bin/env bash

set -e
set -x

# Reset the Prometheus multiprocess metrics dir once per container boot,
# before uvicorn forks any workers (prometheus_client requires this dir be
# empty at process start; doing it per-worker would race, and doing it in
# `prestart` wouldn't help since that's a separate container/filesystem).
multiproc_dir="${PROMETHEUS_MULTIPROC_DIR:-/tmp/prometheus_multiproc_dir}"
rm -rf "$multiproc_dir"
mkdir -p "$multiproc_dir"

exec uvicorn src.main:app --host 0.0.0.0 --port 8000 "$@"
