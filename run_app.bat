@echo off
chcp 65001 >nul
title Salary App - Quan ly luong
cd /d "%~dp0"

REM ============================================================
REM  Chay app quan ly luong (lenh doc lap, ghi log ra run_output.txt)
REM  Dung:  double-click run_app.bat
REM  Xem log:  notepad run_output.txt
REM ============================================================

REM ==== Tim Python that ====
set "PYTHON="
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*" "%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%~D\python.exe" if not defined PYTHON set "PYTHON=%%~D\python.exe"
)
if not defined PYTHON (
    where py >nul 2>nul
    if %errorlevel%==0 set "PYTHON=py"
)
if not defined PYTHON (
    where python >nul 2>nul
    if %errorlevel%==0 set "PYTHON=python"
)
if not defined PYTHON (
    where python3 >nul 2>nul
    if %errorlevel%==0 set "PYTHON=python3"
)
if not defined PYTHON (
    echo [LOI] Khong tim thay Python. Vui long cai Python 3.10+.
    pause
    exit /b 1
)

echo ============================================
echo   Salary App - He thong quan ly luong
echo ============================================
echo  Dung Python: "%PYTHON%"
"%PYTHON%" --version
echo.

REM ==== Kiem tra / cai dependencies ====
"%PYTHON%" -c "import flask, flask_sqlalchemy, flask_login, flask_wtf, wtforms, werkzeug, openpyxl, dotenv" >nul 2>nul
if errorlevel 1 (
    echo Dang cai dat thu vien can thiet...
    "%PYTHON%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [LOI] Cai dat thu vien that bai. Xem chi tiet o run_output.txt
        pause
        exit /b 1
    )
)

REM ==== Khoi dong app, ghi log ====
echo Dang khoi dong app tai: http://127.0.0.1:5000
echo Tai khoan admin mac dinh: admin / admin123
echo.
start "" http://127.0.0.1:5000
"%PYTHON%" run.py > run_output.txt 2>&1

echo.
echo App da dung. Xem log tai run_output.txt
pause
