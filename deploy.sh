#!/usr/bin/env bash
set -euo pipefail

cd /srv/rush-cms-django
POETRY="/home/deploy/.local/bin/poetry"
export POETRY_VIRTUALENVS_IN_PROJECT=true

git pull origin main

$POETRY lock
$POETRY install --no-interaction --no-root

$POETRY run python manage.py migrate
$POETRY run python manage.py collectstatic --noinput

sudo systemctl restart gunicorn.service
