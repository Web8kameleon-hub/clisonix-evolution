#!/usr/bin/env bash
set -euo pipefail
mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"
mc mb -p local/${MINIO_BUCKET} || true
mc policy set public local/${MINIO_BUCKET}

