#!/bin/bash
echo "Starting Hailz Helper (Flask RAG App)..."

export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
