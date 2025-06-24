
FROM python:3.12-slim

LABEL maintainer="mihai@developerakademie.com"
LABEL version="1.0"
LABEL description="Python 3.14.0a7 Alpine 3.21"


RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ffmpeg \
      build-essential \
      libpq-dev \
 && rm -rf /var/lib/apt/lists/*


WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


RUN python manage.py collectstatic --noinput


EXPOSE 8000

# 8. Container starten
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
