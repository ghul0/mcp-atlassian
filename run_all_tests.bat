@echo off
echo Running all tests in virtual environment...
call .venv\Scripts\activate.bat
python tests\run_all_tests.py
pause
