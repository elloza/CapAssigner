# Add pdflatex to Windows PATH permanently
# Run as Administrator: powershell -ExecutionPolicy Bypass -File add_pdflatex_to_path.ps1

Write-Host "Adding pdflatex to Windows PATH..." -ForegroundColor Cyan

# Common MiKTeX installation paths
$possiblePaths = @(
    "C:\Program Files\MiKTeX\miktex\bin\x64",
    "C:\Program Files\MiKTeX 2.9\miktex\bin\x64",
    "C:\Program Files (x86)\MiKTeX\miktex\bin\x64",
    "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\MiKTeX\miktex\bin\x64"
)

# Find where pdflatex is installed
$miktexPath = $null
foreach ($path in $possiblePaths) {
    if (Test-Path "$path\pdflatex.exe") {
        $miktexPath = $path
        Write-Host "Found pdflatex at: $path" -ForegroundColor Green
        break
    }
}

if (-not $miktexPath) {
    Write-Host "pdflatex not found. Please install MiKTeX first:" -ForegroundColor Red
    Write-Host "  Download from: https://miktex.org/download" -ForegroundColor Yellow
    Write-Host "  Or run: choco install miktex -y" -ForegroundColor Yellow
    exit 1
}

# Get current system PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")

# Check if already in PATH
if ($currentPath -like "*$miktexPath*") {
    Write-Host "pdflatex is already in PATH!" -ForegroundColor Green
    Write-Host "  If you just added it, restart your terminal." -ForegroundColor Yellow
    exit 0
}

# Add to system PATH (requires admin)
try {
    $newPath = "$currentPath;$miktexPath"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
    Write-Host "Successfully added to PATH!" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: You must restart your terminal for changes to take effect." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To verify, open a NEW terminal and run:" -ForegroundColor Cyan
    Write-Host "  pdflatex --version" -ForegroundColor White
} catch {
    Write-Host "Failed to add to PATH. This script requires administrator privileges." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run PowerShell as Administrator and try again:" -ForegroundColor Yellow
    Write-Host "  1. Right-click PowerShell and select Run as Administrator" -ForegroundColor White
    Write-Host "  2. Navigate to this folder and run the script again" -ForegroundColor White
    exit 1
}
