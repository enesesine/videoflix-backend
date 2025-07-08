
FROM python:3.12-slim

LABEL maintainer="mihai@developerakademie.com"
LABEL version="1.0"
LABEL description="Python 3.12-slim mit PostgreSQL-Client und ffmpeg"

#
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ffmpeg \
      build-essential \
      libpq-dev \
      postgresql-client \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY backend.entrypoint.sh /app/backend.entrypoint.sh
RUN chmod +x /app/backend.entrypoint.sh

COPY . .


RUN python manage.py collectstatic --noinput


EXPOSE 8000
ENTRYPOINT ["/app/backend.entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]