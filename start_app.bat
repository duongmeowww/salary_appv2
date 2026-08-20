@echo off
chcp 65001 >nul
title Salary App - Quan ly luong
cd /d "%~dp0"

REM ==== Tim Python that (bo qua Windows Store stub) ====
set "PYTHON="

REM 1. Python cai boi installer (duong dan thong dung)
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*" "%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%~D\python.exe" if not defined PYTHON set "PYTHON=%%~D\python.exe"
)

REM 2. py launcher (tranh Windows Store stub)
if not defined PYTHON (
    where py >nul 2>nul
    if %errorlevel%==0 set "PYTHON=py"
)

REM 3. python trong PATH
if not defined PYTHON (
    where python >nul 2>nul
    if %errorlevel%==0 set "PYTHON=python"
)

REM 4. python3 trong PATH
if not defined PYTHON (
    where python3 >nul 2>nul
    if %errorlevel%==0 set "PYTHON=python3"
)

if not defined PYTHON (
    echo [LOI] Khong tim thay Python. Vui long cai Python 3.10+.
    echo Tai: https://www.python.org/downloads/  (nho tick "Add to PATH")
    pause
    exit /b 1
)

REM ==== Kiem tra Python that su chay duoc (tranh Windows Store stub) ====
"%PYTHON%" --version >nul 2>nul
if errorlevel 1 (
    echo [LOI] Phat hien Python gia (Windows Store stub).
    echo Vui long mo Microsoft Store hoac tai https://www.python.org/downloads/
    echo de cai Python 3.10+ that su, roi chay lai file nay.
    pause
    exit /b 1
)

echo ============================================
echo   Salary App - He thong quan ly luong
echo ============================================
"%PYTHON%" --version
echo.

REM ==== Kiem tra / cai dependencies ====
"%PYTHON%" -c "import flask, flask_sqlalchemy, flask_login, flask_wtf, wtforms, werkzeug, openpyxl, dotenv" >nul 2>nul
if errorlevel 1 (
    echo Dang cai dat thu vien can thiet...
    "%PYTHON%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [LOI] Cai dat thu vien that bai.
        pause
        exit /b 1
    )
)

REM ==== Chay app ====
echo Dang khoi dong app tai: http://127.0.0.1:5000
echo Tai khoan admin mac dinh: admin / admin123
echo.
start "" http://127.0.0.1:5000
"%PYTHON%" run.py

pause
