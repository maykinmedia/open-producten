#!/bin/bash

set -e

LOGLEVEL=${CELERY_LOGLEVEL:-INFO}

mkdir -p celerybeat

echo "Starting celery beat"
exec celery --workdir src --app open_producten beat \
    -l $LOGLEVEL \
    -s ../celerybeat/beat