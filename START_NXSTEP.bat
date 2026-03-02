@echo off
setlocal enabledelayedexpansion

echo ==============================================================
echo 🚀 BIENVENUE SUR NXSTEP - SOLUTION UNIFIEE 🚀
echo ==============================================================

:: 1. Lancer le Frontend Next.js (Port 3000)
echo 1/3 Démarrage du Site Web (Frontend)...
start "NXSTEP Frontend (Next.js)" cmd /k "npm run dev"

:: 2. Attendre quelques secondes
timeout /t 5 /nobreak > nul

:: 3. Lancer le Worker Wealth Agent
echo 2/3 Démarrage du Worker IA (Background)...
cd wealth_agent
start "NXSTEP Worker (Backend)" cmd /c "call venv\Scripts\activate.bat && python worker.py"

:: 4. Lancer l'Interface Chat Streamlit
echo 3/3 Démarrage de l'Interface de Gestion (Wealth Agent)...
call venv\Scripts\activate.bat
python -m streamlit run chat_app.py

pause
