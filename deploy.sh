cd /srv/rush-cms-django
git pull origin main
poetry install
poetry run python manage.py makemigrations
poetry run python manage.py migrate
poetry run python manage.py collectstatic --noinput
sudo systemctl restart gunicorn.service
