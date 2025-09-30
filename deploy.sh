#!/usr/bin/env bash
set -euo pipefail

cd /srv/rush-cms-django
PYTHON="/srv/rush-cms-django/.venv/bin/python" # Want project-specific Python virtual environment.
POETRY="/home/deploy/.local/bin/poetry" # BUT must use deployer's Poetry installation (since it only has permission to run that version of Poetry).

git pull origin main

"$POETRY" lock
"$POETRY" install
"$PYTHON" manage.py migrate
"$PYTHON" manage.py collectstatic --noinput
sudo systemctl restart gunicorn.service