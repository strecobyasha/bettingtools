FROM python:3.10-slim

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE "config.settings"

COPY requirements.txt requirements.txt

RUN  mkdir -p /var/www/static/ \
     && mkdir -p /var/www/media/

RUN  apt-get update

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt

COPY . .
COPY arena/static /var/www/static
COPY arena/media /var/www/media

RUN chmod +x entrypoint.sh
ENTRYPOINT ["/opt/app/entrypoint.sh"]
