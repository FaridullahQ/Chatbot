#!/bin/bash

echo "Starting QaderiChat Development Server..."
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup.py first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ".env file not found. Please run setup.py first."
    exit 1
fi

# Start the Django development server
echo "Starting Django development server..."
python manage.py runserver
