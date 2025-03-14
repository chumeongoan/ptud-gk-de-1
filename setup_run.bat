@echo off
echo Setting up Blog Management System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Please install Python 3.7+ and try again.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Initialize database
echo Initializing database...
python init_db.py

REM Start the application
echo Starting application...
echo.
echo Access the application at: http://127.0.0.1:5000/
echo Default admin: admin@example.com / 123
echo.
echo Press Ctrl+C to stop the server
echo.
python app.py

pause