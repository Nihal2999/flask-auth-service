#!/bin/bash
echo "Running migrations..."
flask db upgrade
echo "Starting Flask app with gunicorn..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 run:app