@echo off
title Push NER-LogiX to GitHub
cd /d "%~dp0"

echo ============================================================
echo   Publish NER-LogiX to your GitHub Repository
echo ============================================================
echo.

set /p REPO_URL="Enter your GitHub Repository URL (e.g. https://github.com/username/ner-logix.git): "

if "%REPO_URL%"=="" (
    echo [ERROR] No repository URL provided. Exiting.
    pause
    exit /b 1
)

echo.
echo Setting remote origin to: %REPO_URL%
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo.
echo Pushing branch 'main' to GitHub...
git branch -M main
git push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo ============================================================
    echo   SUCCESS! NER-LogiX published to GitHub successfully!
    echo ============================================================
) else (
    echo.
    echo [NOTE] If prompted for authentication, enter your GitHub Personal Access Token (PAT) as password.
)

pause
