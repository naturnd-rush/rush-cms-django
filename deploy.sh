#!/usr/bin/env bash
set -euo pipefail

# Cd to project and pull
cd /srv/rush-cms-django
echo "Pulling repository from $(pwd)..."
git pull origin main

# Make sure we use the correct poetry environment
POETRY="/home/deploy/.local/bin/poetry"
export POETRY_VIRTUALENVS_IN_PROJECT=true
$($POETRY env activate)
echo "Deploying with virtualenv: $($POETRY env info --path)"

# Install any new dependencies
$POETRY install --no-interaction --no-root

# Migrate Django and collect static
$POETRY run python manage.py migrate
$POETRY run python manage.py collectstatic --noinput

# Restart Gunicorn service!
sudo systemctl restart gunicorn.service
