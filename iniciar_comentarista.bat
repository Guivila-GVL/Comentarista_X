@echo off
title Comentarista - Asistente Editorial para X
color 0B
echo ========================================================
echo   PROYECTO COMENTARISTA (2026)
echo   Asistente Editorial para X con Integracion Grafana
echo ========================================================
echo.
cd /d "%~dp0"

echo [1/2] Abriendo navegador en http://localhost:8000...
start "" http://localhost:8000

echo [2/2] Iniciando servidor local en http://127.0.0.1:8000...
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause
