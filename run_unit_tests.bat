@echo off
echo Running unit tests in virtual environment...
call .venv\Scripts\activate.bat
python tests\run_unit_tests.py
pause
