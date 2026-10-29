@echo off
title Launching Multimodal AI Chatbot...
echo ===================================================
echo     MULTIMODAL AI CHATBOT (3D GOLDEN EDITION)
echo ===================================================
echo.
echo 1. Launching Backend (Port 8000)...
start "Chatbot Backend - Port 8000" cmd /k "%~dp0start_backend.bat"

echo 2. Launching Frontend (Port 5173)...
start "Chatbot Frontend - Port 5173" cmd /k "%~dp0start_frontend.bat"

echo.
echo Both servers are starting up!
echo Opening browser in 5 seconds at http://127.0.0.1:5173...
timeout /t 5 /nobreak >nul
start http://127.0.0.1:5173
echo Done! Enjoy using your AI Chatbot.
