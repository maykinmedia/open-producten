#!/bin/sh
#
# Generate the API schema from the code into the output file.
#
# Run this script from the root of the repository:
#
#   ./bin/generate_api_schema.sh [outfile]
#
# 'outfile' defaults to `src/openapi.yml`
#
# For multiple-major version support, take a look at the objects-api and tweak
# accordingly.
#
set -eu -o pipefail

OUTFILE=${1:-src/openapi.yaml}

src/manage.py spectacular \
    --validate \
    --fail-on-warn \
    --lang=en \
    --file "$OUTFILE"
