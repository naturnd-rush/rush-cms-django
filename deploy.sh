#!/usr/bin/env bash
set -euo pipefail

# Cd to project and pull
cd /srv/rush-cms-django
git pull origin main

# MAke sure we use the correct poetry environment
POETRY="/home/deploy/.local/bin/poetry"
export POETRY_VIRTUALENVS_IN_PROJECT=true
$POETRY env use "/srv/rush-cms-django/.venv/bin/python"
$POETRY env info

# Install any new dependencies
$POETRY lock
$POETRY install --no-interaction --no-root

# Migrate Django and collect static
$POETRY run python manage.py migrate
$POETRY run python manage.py collectstatic --noinput

# Restart Gunicorn service!
sudo systemctl restart gunicorn.service
