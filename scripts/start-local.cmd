@echo off
setlocal
cd /d "%~dp0.."
python -m pip install -r requirements.txt
python init_db.py
python seed_demo.py
python smoke_test.py
endlocal
