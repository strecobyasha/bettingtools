#!/bin/bash

exec  gunicorn config.wsgi:application -c /opt/app/gunicorn.conf.py & celery -A celery_tasks worker -l info -B

"$@"
