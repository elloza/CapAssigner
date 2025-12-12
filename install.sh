#!/bin/bash
# Installation script for CapAssigner
# Installs Python dependencies and LaTeX for circuit rendering

set -e

echo "=================================="
echo "CapAssigner Installation"
echo "=================================="

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install LaTeX for lcapy
echo ""
echo "Checking LaTeX installation..."
python install_latex.py --check-only

if [ $? -ne 0 ]; then
    echo ""
    read -p "LaTeX (pdflatex) is not installed. Install it now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python install_latex.py
    else
        echo "Skipping LaTeX installation."
        echo "Note: Circuit diagrams will use matplotlib fallback rendering."
    fi
fi

echo ""
echo "=================================="
echo "Installation complete!"
echo "=================================="
echo ""
echo "To run the application:"
echo "  streamlit run app.py"
