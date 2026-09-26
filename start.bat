@echo off
title NER-LogiX Logistics Intelligence Platform
cd /d "%~dp0"

echo ===========================================================
echo  NER-LogiX: North Eastern Logistics Intelligence Platform
echo  AI-Powered Accessibility ^& Disruption Management
echo ===========================================================

set PYTHON_EXE="%~dp0python_env\python.exe"
if not exist %PYTHON_EXE% (
    set PYTHON_EXE=python
)

echo Starting NER-LogiX Server on http://localhost:8080 ...
start http://localhost:8080

%PYTHON_EXE% "%~dp0server.py" 8080
pause
