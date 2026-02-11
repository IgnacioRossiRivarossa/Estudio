#!/usr/bin/env bash
# exit on error
set -o errexit

# Navigate to Django project directory
cd $(dirname $(find . | grep manage.py$))

# Run gunicorn server
gunicorn $(dirname $(find . | grep wsgi.py$) | sed "s/\.\///g").wsgi:application
