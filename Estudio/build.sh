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
python manage.py createsuperuser --username admin --email "ignaciorossi@rivarossa.com" --noinput || true
