@echo off
cd backend
call venv\Scripts\activate
:: Agregamos el directorio actual al PYTHONPATH para que encuentre los módulos
set PYTHONPATH=%PYTHONPATH%;%CD%
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause