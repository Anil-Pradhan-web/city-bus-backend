#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Optional: Repopulate data if needed (comment out if dangerous for prod)
# python manage.py repopulate_transport_data
