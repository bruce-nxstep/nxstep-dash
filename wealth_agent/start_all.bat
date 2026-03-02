@echo off
echo ==============================================================
echo 🚀 Lancement de l'Agence Lead Gen (NXSTEP Wealth Agent) 🚀
echo ==============================================================

cd /d "%~dp0"
call venv\Scripts\activate.bat

echo 1/2 Demarrage du Worker en arriere-plan...
start "NXSTEP Worker (NE PAS FERMER)" cmd /c "call venv\Scripts\activate.bat && python worker.py"

echo 2/2 Démarrage de l'Interface de Chat...
python -m streamlit run chat_app.py
pause
