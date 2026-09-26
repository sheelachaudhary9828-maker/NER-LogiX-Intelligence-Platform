@echo off
title Push NER-LogiX to GitHub
cd /d "%~dp0"

echo ============================================================
echo   Publishing NER-LogiX to GitHub Repository
echo   Target: https://github.com/sheelachaudhary9828-maker/NER-LogiX-Intelligence-Platform.git
echo ============================================================
echo.

set PATH=%LOCALAPPDATA%\Programs\Git\cmd;%PATH%

git remote remove origin 2>nul
git remote add origin https://github.com/sheelachaudhary9828-maker/NER-LogiX-Intelligence-Platform.git

echo Branch: main
git branch -M main

echo.
echo Pushing code to GitHub...
echo (If prompted, click "Sign in with your browser" or enter your GitHub Personal Access Token)
echo.

git push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo ============================================================
    echo   SUCCESS! NER-LogiX published to GitHub successfully!
    echo ============================================================
) else (
    echo.
    echo [NOTE] Push requires GitHub authentication.
    echo You can generate a Personal Access Token at https://github.com/settings/tokens
)

pause
