@echo off
echo Starting Resume Skill Gap Analyzer...
cd /d "%~dp0"
cd backend
python -m app.main
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Could not start the backend. 
    echo Make sure you are in the project root and have installed the requirements.
    pause
)
