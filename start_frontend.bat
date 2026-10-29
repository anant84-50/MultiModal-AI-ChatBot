@echo off
title Multimodal AI Chatbot - Frontend
echo ===================================================
echo Starting React Vite Frontend (Port 5173)...
echo ===================================================
cd /d "%~dp0frontend"

if not exist "node_modules\" (
    echo [First-Time Setup] Installing frontend npm dependencies...
    call npm install
)

npm run dev -- --host 127.0.0.1 --port 5173
pause
