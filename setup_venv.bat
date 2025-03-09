@echo off
echo Setting up virtual environment...

:: Create virtual environment if it doesn't exist
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Install package in development mode
echo Installing package in development mode...
pip install -e .

echo Virtual environment setup completed successfully!
