#!/usr/bin/env bash
set -euo pipefail

cd /srv/rush-cms-django
git pull origin main
/home/deploy/.local/bin/poetry lock
/home/deploy/.local/bin/poetry install
#poetry run python manage.py makemigrations <-- migrations should always be added by git
/home/deploy/.local/bin/poetry run python manage.py migrate
/home/deploy/.local/bin/poetry run python manage.py collectstatic --noinput
sudo systemctl restart gunicorn.service
