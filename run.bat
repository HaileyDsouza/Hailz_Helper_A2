@echo off
echo Starting Hailz Helper (Flask RAG App)...

set FLASK_APP=app.py
set FLASK_ENV=development

flask run --host=0.0.0.0 --port=5000
pause
