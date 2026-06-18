@echo off
cd /d "%~dp0"

set UPLOAD_PASSWORD=123456
set MAX_UPLOAD_MB=20000
set VERBOSE_LOG=1

if not exist ".venv\Scripts\python.exe" (
    echo Sanal ortam bulunamadi.
    echo Once su komutlari calistirin:
    echo python -m venv .venv
    echo .\.venv\Scripts\activate
    echo pip install -r requirements.txt
    pause
    exit /b
)

".venv\Scripts\python.exe" app.py
pause