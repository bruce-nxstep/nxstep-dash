@echo off
echo ==============================================
echo Lancement de l'Agent NXSTEP (Interface Conversationnelle)
echo ==============================================
cd /d "%~dp0"
call venv\Scripts\activate.bat
python -m streamlit run chat_app.py
pause
