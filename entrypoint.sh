#!/bin/sh
echo "Collecting static..."
python manage.py collectstatic --noinput

exec "$@"
