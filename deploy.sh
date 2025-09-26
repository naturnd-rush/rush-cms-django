#!/usr/bin/bash

cd /srv/rush-cms-django
git pull origin main
poetry lock
poetry install
#poetry run python manage.py makemigrations <-- migrations should always be added by git
poetry run python manage.py migrate
poetry run python manage.py collectstatic --noinput
sudo systemctl restart gunicorn.service
