@echo off
REM ============================================
REM GPU Training Setup Script for GT 1030
REM NVIDIA CUDA + PyTorch Installation
REM ============================================

echo.
echo [*] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan. Install Python 3.9+ terlebih dahulu.
    pause
    exit /b 1
)

echo [OK] Python found

echo.
echo [*] Checking NVIDIA GPU and CUDA...
nvidia-smi >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] nvidia-smi tidak ditemukan. Pastikan NVIDIA Driver sudah terinstall.
    echo Visit: https://www.nvidia.com/Download/driverDetails.aspx
    pause
) else (
    echo [OK] NVIDIA Driver detected
    nvidia-smi
)

echo.
echo [*] Updating pip...
python -m pip install --upgrade pip setuptools wheel

echo.
echo [*] Installing PyTorch with CUDA 12.1 support...
echo This may take a few minutes...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo.
echo [*] Installing project dependencies...
pip install -r requirements.txt

echo.
echo [*] Installing DeepSpeed (optional but recommended)...
pip install deepspeed==0.10.0

echo.
echo [*] Verifying CUDA support...
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}'); import torch; [print(f'Device {i}: {torch.cuda.get_device_name(i)}') for i in range(torch.cuda.device_count())]"

echo.
echo [SUCCESS] GPU setup complete!
echo.
echo Next steps:
echo 1. Run training: python train.py --epochs 5 --batch 8 --config tiny
echo 2. Or with DeepSpeed: python train.py --epochs 5 --batch 4 --deepspeed
echo 3. See GPU_SETUP.md for detailed guide and troubleshooting
echo.
pause
