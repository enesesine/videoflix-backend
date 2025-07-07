#!/usr/bin/env bash
set -e

# Migrate first
python manage.py migrate --noinput

# ----- Create superuser IF none exists -----------------------------
if [ "$DJANGO_SUPERUSER_EMAIL" ] && \
   ! python manage.py shell -c \
      "from django.contrib.auth import get_user_model as g; \
       print(1 if g().objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists() else 0)" | grep -q 1
then
    echo "• Creating initial superuser $DJANGO_SUPERUSER_EMAIL …"
    python manage.py createsuperuser \
        --email "$DJANGO_SUPERUSER_EMAIL" \
        --noinput

    # Passwort setzen, falls env-Var existiert
    if [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
        python manage.py shell - <<PY
from django.contrib.auth import get_user_model
u = get_user_model().objects.get(email="$DJANGO_SUPERUSER_EMAIL")
u.set_password("$DJANGO_SUPERUSER_PASSWORD")
u.save()
print("✔ Superuser password set")
PY
    fi
fi
# -------------------------------------------------------------------

# finally: start gunicorn / runserver
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000
