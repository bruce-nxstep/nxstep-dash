@echo off
echo ==============================================
echo Lancement de l'Agent NXSTEP (Generation de Leads)
echo ==============================================
cd /d "%~dp0"
call venv\Scripts\activate.bat
python main.py
pause
