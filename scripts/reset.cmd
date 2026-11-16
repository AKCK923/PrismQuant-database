@echo off
setlocal
cd /d "%~dp0.."
python init_db.py --reset
python seed_demo.py
python smoke_test.py
endlocal
