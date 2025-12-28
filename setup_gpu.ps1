# ============================================
# GPU Training Setup Script for GT 1030
# NVIDIA CUDA + PyTorch Installation
# PowerShell Version
# ============================================

Write-Host "`n[*] Checking Python installation..." -ForegroundColor Cyan
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Python tidak ditemukan. Install Python 3.9+ terlebih dahulu." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green

Write-Host "`n[*] Checking NVIDIA GPU and CUDA..." -ForegroundColor Cyan
try {
    nvidia-smi 2>$null | Out-Null
    Write-Host "[OK] NVIDIA Driver detected" -ForegroundColor Green
    nvidia-smi | Write-Host
} catch {
    Write-Host "[WARNING] nvidia-smi tidak ditemukan atau NVIDIA Driver tidak terinstall" -ForegroundColor Yellow
    Write-Host "Visit: https://www.nvidia.com/Download/driverDetails.aspx" -ForegroundColor Yellow
}

Write-Host "`n[*] Updating pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip setuptools wheel

Write-Host "`n[*] Installing PyTorch with CUDA 12.1 support..." -ForegroundColor Cyan
Write-Host "This may take a few minutes..." -ForegroundColor Yellow
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

Write-Host "`n[*] Installing project dependencies..." -ForegroundColor Cyan
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
} else {
    Write-Host "[WARNING] requirements.txt not found, skipping" -ForegroundColor Yellow
}

Write-Host "`n[*] Installing DeepSpeed (optional but recommended)..." -ForegroundColor Cyan
pip install deepspeed==0.10.0

Write-Host "`n[*] Verifying CUDA support..." -ForegroundColor Cyan
$verifyScript = @"
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    for i in range(torch.cuda.device_count()):
        print(f'Device {i}: {torch.cuda.get_device_name(i)}')
        props = torch.cuda.get_device_properties(i)
        print(f'  Total Memory: {props.total_memory / 1e9:.1f} GB')
else:
    print('[WARNING] CUDA not available. Check driver installation.')
"@
python -c $verifyScript

Write-Host "`n[SUCCESS] GPU setup complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Run training: python train.py --epochs 5 --batch 8 --config tiny"
Write-Host "2. Or with DeepSpeed: python train.py --epochs 5 --batch 4 --deepspeed"
Write-Host "3. See GPU_SETUP.md for detailed guide and troubleshooting"
Write-Host ""
Read-Host "Press Enter to exit"
