#!/bin/sh
set -eu
python -m app.infrastructure.migrate
exec python -m uvicorn app.bootstrap:app --host 0.0.0.0 --port "${PORT:-8080}"
