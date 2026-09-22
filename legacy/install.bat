@echo off
REM Installation script for CapAssigner (Windows)
REM Installs Python dependencies and LaTeX for circuit rendering

echo ==================================
echo CapAssigner Installation
echo ==================================

REM Install Python dependencies
echo.
echo Installing Python dependencies...
pip install -r requirements.txt

REM Install LaTeX for lcapy
echo.
echo Checking LaTeX installation...
python install_latex.py --check-only

if errorlevel 1 (
    echo.
    choice /C YN /M "LaTeX (pdflatex) is not installed. Install it now?"
    if errorlevel 2 goto skip_latex
    if errorlevel 1 goto install_latex
)
goto end

:install_latex
python install_latex.py
goto end

:skip_latex
echo Skipping LaTeX installation.
echo Note: Circuit diagrams will use matplotlib fallback rendering.

:end
echo.
echo ==================================
echo Installation complete!
echo ==================================
echo.
echo To run the application:
echo   streamlit run app.py
pause
