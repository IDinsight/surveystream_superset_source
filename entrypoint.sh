#!/bin/bash

set -e
echo "Starting"

case "$1" in
  webserver)

	export FLASK_APP=superset
	
	# Initialize the database
	superset db upgrade

	# Create default roles and permissions
	superset init
	# Create an admin user
	flask fab create-admin --username "${INIT_SUPERSET_USER}" --firstname "${INIT_SUPERSET_FIRSTNAME}" --lastname "${INIT_SUPERSET_LASTNAME}" --email "${INIT_SUPERSET_EMAIL}" --password "${INIT_SUPERSET_PASS}"
  
	gunicorn -w 10 \
      --worker-class gevent \
      --worker-connections 1000 \
      --timeout 120 \
      --limit-request-line 0 \
      --limit-request-field_size 0 \
      "superset.app:create_app()"
	;;
  worker)

	echo "In worker container"
    celery -A superset.tasks.celery_app worker --pool=gevent --concurrency=4
    ;;
  flower)

	echo "In flower container"
    celery  -A superset.tasks.celery_app flower
    ;;
  beat)

	echo "In scheduler container"
    celery  -A superset.tasks.celery_app beat --pidfile /tmp/celerybeat.pid --schedule /tmp/celerybeat-schedule 
    ;;
esac
