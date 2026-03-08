#!/bin/bash
echo "Running migrations..."
flask db upgrade
echo "Starting Flask app..."
exec python run.py