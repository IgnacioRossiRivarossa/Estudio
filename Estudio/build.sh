#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r ./requirements.txt

# Navigate to Django project directory
cd $(dirname $(find . | grep manage.py$))

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Create superuser (only if it doesn't exist)
# Note: Requiere variables de entorno: DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD, 
# DJANGO_SUPERUSER_NOMBRE, DJANGO_SUPERUSER_APELLIDO
python manage.py createsuperuser --email "${DJANGO_SUPERUSER_EMAIL}" --noinput || true
