@echo off
cd /d "%~dp0"
call backend\venv\Scripts\activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
pause
