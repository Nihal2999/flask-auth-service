#!/bin/bash
echo "Running migrations..."
flask db upgrade
echo "Starting Flask app with gunicorn..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 run:app