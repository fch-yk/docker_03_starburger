#!/bin/sh
echo "Collecting static..."
python manage.py collectstatic --noinput
python manage.py migrate --noinput

exec "$@"
