@echo off
cd /d C:\Project\cdms_backend\cdms2

REM Create directories if they don't exist
if not exist private_media mkdir private_media
if not exist watermarks mkdir watermarks
if not exist media1 mkdir media1
if not exist static2 mkdir static2

echo ✅ Directories created

REM Activate virtual environment
call .venv_py37\Scripts\activate.bat

REM Run Django server
echo Starting Django Server...
python manage.py runserver 8000
pause
