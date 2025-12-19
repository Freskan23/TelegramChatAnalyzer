@echo off
title Telegram Chat Analyzer - Instalador

echo.
echo ========================================================
echo      TELEGRAM CHAT ANALYZER - INSTALADOR
echo ========================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado.
    echo         Descargalo de https://python.org
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

:: Create venv if not exists
if not exist "venv" (
    echo [1/3] Creando entorno virtual...
    python -m venv venv
) else (
    echo [1/3] Entorno virtual ya existe
)

:: Activate and install
echo [2/3] Instalando dependencias...
call venv\Scripts\activate
pip install -q -r requirements.txt

echo [3/3] Instalacion completada!
echo.
echo ========================================================
echo.
echo   Para ejecutar la aplicacion:
echo   - Doble clic en EJECUTAR.bat
echo.
echo   O desde la terminal:
echo   - venv\Scripts\activate
echo   - python TelegramChatAnalyzer.py
echo.
echo ========================================================
echo.
pause
