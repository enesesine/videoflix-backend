#!/bin/sh
set -e

echo "⏳ Warte auf PostgreSQL auf $DB_HOST:$DB_PORT…"
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -q; do
  echo "PostgreSQL nicht erreichbar – warte 1 Sekunde"
  sleep 1
done
echo "✅ PostgreSQL ist da – fahre fort…"

echo "📦 Sammle statische Dateien…"
python manage.py collectstatic --noinput

echo "🔄 Wende Migrations an…"
python manage.py makemigrations
python manage.py migrate --noinput

 echo " Lege Superuser an (falls nötig)…"
 python manage.py shell <<PYCODE
import os, sys
from django.contrib.auth import get_user_model
User = get_user_model()

email    = os.getenv('DJANGO_SUPERUSER_EMAIL')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
username = os.getenv('DJANGO_SUPERUSER_USERNAME', email)

if not email or not password:
    sys.exit("✖ DJANGO_SUPERUSER_EMAIL / _PASSWORD fehlt in der .env!")

if not User.objects.filter(email__iexact=email).exists():
    User.objects.create_superuser(email=email, password=password)
    print("✓ Superuser angelegt:", email)
else:
    print("✓ Superuser existiert bereits:", email)
PYCODE

echo "🚀 Starte Gunicorn…"
exec gunicorn core.wsgi:application -b 0.0.0.0:8000
