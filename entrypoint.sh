#!/bin/sh
set -e

poetry run alembic upgrade head

exec poetry run uvicorn direitos.app:app --app-dir src --host 0.0.0.0 --port 8000 --reload