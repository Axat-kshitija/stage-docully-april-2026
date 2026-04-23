@echo off
REM Django Server Startup Script
cd /d C:\Project\cdms_backend\cdms2

echo.
echo ============================================
echo Creating required directories...
echo ============================================
if not exist private_media mkdir private_media
if not exist watermarks mkdir watermarks  
if not exist media1 mkdir media1
if not exist static2 mkdir static2
echo ✅ Directories ready

echo.
echo ============================================
echo Activating Python environment...
echo ============================================
call .venv_py37\Scripts\activate.bat

echo.
echo ============================================
echo Starting Django Server on port 8000
echo ============================================
echo.
echo 🚀 Server will be available at:
echo    http://127.0.0.1:8000/projectName/admin/
echo.
echo Press CTRL+C to stop the server
echo.

python manage.py runserver 8000

pause
