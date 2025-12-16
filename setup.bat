@echo off
REM Office Desk Booking System - Quick Setup Script for Windows

echo Setting up Office Desk Booking System...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.13+ first.
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv .venv

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Setup complete!
echo.
echo To start the application:
echo   1. Activate the virtual environment: .venv\Scripts\activate
echo   2. Run the server: python app.py
echo   3. Open your browser to: http://127.0.0.1:5001
echo.
echo Happy booking!
pause
