#!/usr/bin/env bash
set -e

# Helper script to create venv, install deps, migrate, create superuser (interactive), and import sample questions
cd "$(dirname "$0")"

if [ -z "$VIRTUAL_ENV" ]; then
  python -m venv .venv
  source .venv/bin/activate
else
  echo "Using existing virtualenv"
fi

pip install --upgrade pip
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate

echo "Now run: python manage.py createsuperuser to create an admin user"

echo "To import questions.run: python manage.py import_questions --file ../questions.xlsx"

echo "Setup complete. Start the server with: python manage.py runserver"
