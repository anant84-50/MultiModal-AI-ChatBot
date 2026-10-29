@echo off
title Multimodal AI Chatbot - Backend
echo ===================================================
echo Starting FastAPI Backend Server (Port 8000)...
echo ===================================================
cd /d "%~dp0backend"

if not exist "venv\Scripts\activate.bat" (
    echo [First-Time Setup] Creating Python virtual environment...
    python -m venv venv
    call .\venv\Scripts\activate
    echo [First-Time Setup] Installing required Python libraries...
    pip install -r requirements.txt
) else (
    call .\venv\Scripts\activate
)

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
