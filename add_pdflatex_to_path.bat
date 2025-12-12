@echo off
REM Add pdflatex to Windows PATH permanently
REM Run as Administrator

echo Adding pdflatex to Windows PATH...

REM Check common MiKTeX installation paths
set MIKTEX_PATH=
if exist "C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe" (
    set MIKTEX_PATH=C:\Program Files\MiKTeX\miktex\bin\x64
)
if exist "C:\Program Files (x86)\MiKTeX\miktex\bin\x64\pdflatex.exe" (
    set MIKTEX_PATH=C:\Program Files (x86)\MiKTeX\miktex\bin\x64
)
if exist "%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe" (
    set MIKTEX_PATH=%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64
)

if "%MIKTEX_PATH%"=="" (
    echo [ERROR] pdflatex not found. Please install MiKTeX first:
    echo   Download from: https://miktex.org/download
    echo   Or run: choco install miktex -y
    pause
    exit /b 1
)

echo Found pdflatex at: %MIKTEX_PATH%

REM Add to system PATH (requires admin)
setx /M PATH "%PATH%;%MIKTEX_PATH%" >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Added to PATH!
    echo.
    echo IMPORTANT: You must restart your terminal for changes to take effect.
    echo.
    echo To verify, open a NEW terminal and run:
    echo   pdflatex --version
) else (
    echo [ERROR] Failed to add to PATH. This requires administrator privileges.
    echo.
    echo Please run this script as Administrator:
    echo   1. Right-click this file
    echo   2. Select "Run as administrator"
)

pause
