@echo off
echo Starting QaderiChat Development Server...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Please run setup.py first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate

REM Check if .env file exists
if not exist ".env" (
    echo .env file not found. Please run setup.py first.
    pause
    exit /b 1
)

REM Start the Django development server
echo Starting Django development server...
python manage.py runserver

pause
