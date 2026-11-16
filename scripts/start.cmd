@echo off
setlocal
cd /d "%~dp0.."
docker compose up -d
python -m pip install -r requirements.txt
python init_db.py
python seed_demo.py
python smoke_test.py
endlocal
