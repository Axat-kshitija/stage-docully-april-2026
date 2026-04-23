@echo off
REM Start Django Development Server

cd /d C:\Project\cdms_backend\cdms2

REM Activate virtual environment
call .venv_py37\Scripts\activate.bat

REM Run Django server
echo.
echo ============================================
echo Starting Django Server on port 8000
echo ============================================
echo.
python manage.py runserver 8000

pause
