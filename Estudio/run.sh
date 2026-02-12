#!/usr/bin/env bash
# exit on error
set -o errexit

# Navigate to Django project directory
cd $(dirname $(find . | grep manage.py$))

# Run gunicorn server with increased timeout for email operations
gunicorn --timeout 60 $(dirname $(find . | grep wsgi.py$) | sed "s/\.\///g").wsgi:application
