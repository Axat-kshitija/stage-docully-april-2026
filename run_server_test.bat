@echo off
REM Activate virtual environment
call .venv_py37\Scripts\activate.bat

REM Run Django server
python manage.py runserver
