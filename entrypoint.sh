#!/bin/bash

python3 manage.py collectstatic --noinput --no-input --clear

python3 manage.py makemigrations main

python3 manage.py migrate

python3 manage.py init_config

python3 manage.py load_translations translations.json --force

exec "$@"