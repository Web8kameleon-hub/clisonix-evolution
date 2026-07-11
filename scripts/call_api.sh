#!/usr/bin/env bash
set -euo pipefail

TOKEN=${1:?"token required"}
PATH_SUFFIX=${2:?"path required"}
HOST=${API_HOST:-http://localhost:8000}

curl -s \
  -H "Authorization: Bearer ${TOKEN}" \
  "${HOST}${PATH_SUFFIX}" | jq

