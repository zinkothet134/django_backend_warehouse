#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Bundle static files for WhiteNoise
python manage.py collectstatic --no-input

# Apply django-tenants migrations to both public and all tenant schemas
python manage.py migrate_schemas

