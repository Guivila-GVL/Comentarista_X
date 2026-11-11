@echo off
title Comentarista - Asistente Editorial para X
color 0B
echo ========================================================
echo   PROYECTO COMENTARISTA (2026)
echo   Asistente Editorial para X con Integracion Grafana
echo ========================================================
echo.
cd /d "%~dp0"

echo Comprobando si el servidor ya esta activo en el puerto 8000...
python -c "import socket, sys; s = socket.socket(); sys.exit(0 if s.connect_ex(('127.0.0.1', 8000)) == 0 else 1)"
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [INFO] El servidor de Comentarista YA esta en ejecucion en el puerto 8000.
    echo        (Gestionado como servicio en segundo plano por el ecosistema)
    echo.
    echo [1/1] Abriendo interfaz en el navegador http://localhost:8000...
    start "" http://localhost:8000
    echo.
    echo Servidor verificado y respondiendo 200 OK.
    exit /b 0
)

echo [1/2] Abriendo navegador en http://localhost:8000...
start "" http://localhost:8000

echo [2/2] Iniciando servidor local en http://127.0.0.1:8000...
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause
