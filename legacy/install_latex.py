#!/usr/bin/env python3
"""
Install LaTeX (pdflatex) for lcapy circuit rendering.

This script detects the OS and installs the appropriate LaTeX distribution:
- Linux (Debian/Ubuntu): texlive-latex-base + texlive-latex-extra
- Linux (RHEL/CentOS/Fedora): texlive-latex
- Linux (Arch): texlive-core
- macOS: BasicTeX via brew
- Windows: MiKTeX via chocolatey or manual download

Usage:
    python install_latex.py
    python install_latex.py --check-only  # Just check if pdflatex is available
"""

import sys
import platform
import subprocess
import shutil
from pathlib import Path


def check_pdflatex():
    """Check if pdflatex is already installed."""
    return shutil.which('pdflatex') is not None


def run_command(cmd, shell=False, check=True):
    """Run a shell command and return success status."""
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            check=check,
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        return False
    except FileNotFoundError:
        return False


def install_linux():
    """Install LaTeX on Linux."""
    system = platform.system()
    
    # Detect Linux distribution
    try:
        with open('/etc/os-release') as f:
            os_info = f.read().lower()
    except FileNotFoundError:
        os_info = ""
    
    if 'debian' in os_info or 'ubuntu' in os_info:
        print("Detected Debian/Ubuntu...")
        print("Installing texlive-latex-base and texlive-latex-extra...")
        cmd = ['sudo', 'apt-get', 'update']
        if run_command(cmd):
            cmd = ['sudo', 'apt-get', 'install', '-y', 'texlive-latex-base', 'texlive-latex-extra']
            return run_command(cmd)
    
    elif 'rhel' in os_info or 'centos' in os_info or 'fedora' in os_info:
        print("Detected RHEL/CentOS/Fedora...")
        print("Installing texlive-latex...")
        cmd = ['sudo', 'yum', 'install', '-y', 'texlive-latex']
        return run_command(cmd)
    
    elif 'arch' in os_info:
        print("Detected Arch Linux...")
        print("Installing texlive-core...")
        cmd = ['sudo', 'pacman', '-S', '--noconfirm', 'texlive-core']
        return run_command(cmd)
    
    else:
        print("Unknown Linux distribution.")
        print("Please install LaTeX manually:")
        print("  Debian/Ubuntu: sudo apt-get install texlive-latex-base texlive-latex-extra")
        print("  RHEL/CentOS:   sudo yum install texlive-latex")
        print("  Arch:          sudo pacman -S texlive-core")
        return False


def install_macos():
    """Install LaTeX on macOS."""
    print("Detected macOS...")
    
    # Check if Homebrew is installed
    if not shutil.which('brew'):
        print("Homebrew not found. Please install Homebrew first:")
        print("  /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        return False
    
    print("Installing BasicTeX via Homebrew...")
    cmd = ['brew', 'install', '--cask', 'basictex']
    if run_command(cmd):
        print("\nBasicTeX installed. You may need to update your PATH:")
        print("  export PATH=\"/Library/TeX/texbin:$PATH\"")
        return True
    return False


def install_windows():
    """Install LaTeX on Windows."""
    print("Detected Windows...")
    
    # Check if Chocolatey is installed
    if shutil.which('choco'):
        print("Installing MiKTeX via Chocolatey...")
        print("Note: This requires administrator privileges.")
        cmd = 'choco install miktex -y'
        success = run_command(cmd, shell=True, check=False)
        
        if success:
            print("\nMiKTeX installed. You may need to:")
            print("  1. Restart your terminal")
            print("  2. Or add to PATH: C:\\Program Files\\MiKTeX\\miktex\\bin\\x64\\")
            return True
        else:
            print("\nChocolatey installation failed (may need admin rights).")
    
    print("\nPlease install MiKTeX manually:")
    print("  1. Download from: https://miktex.org/download")
    print("  2. Run the installer")
    print("  3. Restart your terminal")
    print("\nOr install Chocolatey first (https://chocolatey.org/) and run:")
    print("  choco install miktex -y")
    return False


def main():
    """Main installation logic."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Install LaTeX for lcapy rendering')
    parser.add_argument('--check-only', action='store_true', 
                       help='Only check if pdflatex is available')
    args = parser.parse_args()
    
    print("=" * 60)
    print("LaTeX (pdflatex) Installation for lcapy")
    print("=" * 60)
    
    # Check if already installed
    if check_pdflatex():
        print("\n✓ pdflatex is already installed!")
        try:
            result = subprocess.run(['pdflatex', '--version'], 
                                   capture_output=True, text=True)
            print(result.stdout.split('\n')[0])
        except Exception:
            pass
        return 0
    
    print("\n✗ pdflatex is not installed.")
    
    if args.check_only:
        print("\nNote: Lcapy will fall back to matplotlib rendering without pdflatex.")
        return 1
    
    # Detect OS and install
    system = platform.system()
    
    print(f"\nDetected OS: {system}")
    print("Attempting to install LaTeX...\n")
    
    success = False
    if system == 'Linux':
        success = install_linux()
    elif system == 'Darwin':
        success = install_macos()
    elif system == 'Windows':
        success = install_windows()
    else:
        print(f"Unsupported OS: {system}")
        return 1
    
    # Verify installation
    print("\n" + "=" * 60)
    if success and check_pdflatex():
        print("✓ LaTeX installed successfully!")
        print("\nYou may need to restart your terminal for PATH changes to take effect.")
        return 0
    else:
        print("✗ Installation incomplete or failed.")
        print("\nNote: Lcapy will fall back to matplotlib rendering without pdflatex.")
        print("The application will still work, but circuit diagrams will use simpler rendering.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
