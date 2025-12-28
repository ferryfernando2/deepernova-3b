# GPU Training Setup Guide (NVIDIA GT 1030)

## Persyaratan
- **GPU:** NVIDIA GT 1030 (2GB VRAM) atau lebih tinggi
- **Driver:** NVIDIA driver terbaru (versi ≥ 470)
- **CUDA:** CUDA 11.8 atau 12.1
- **cuDNN:** 8.7+

## Langkah Setup

### 1. Install NVIDIA Driver & CUDA Toolkit

```powershell
# Download dari: https://www.nvidia.com/Download/driverDetails.aspx
# Pilih: Product Type = GeForce, Product Series = GeForce GT 10 Series, Product = GeForce GT 1030

# Atau gunakan NVIDIA Studio Driver:
# https://www.nvidia.com/Download/driverDetails.aspx (filter by GT 1030)
```

### 2. Verifikasi CUDA Installation

```powershell
nvcc --version
```

### 3. Install PyTorch dengan CUDA Support

Pilih salah satu (untuk CUDA 12.1):

```powershell
# Option A: Pip install
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Option B: Conda install (jika menggunakan Anaconda)
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
```

### 4. Install Dependencies dengan GPU Support

```powershell
pip install -r requirements.txt
pip install deepspeed==0.10.0
```

### 5. Verifikasi GPU Detection

```powershell
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0)}')"
```

## Training dengan GPU

### Option A: Standard Training (CPU default, tapi auto-detect GPU)

```powershell
python train.py --epochs 5 --batch 8 --config tiny
```

Script otomatis akan deteksi GPU dan menggunakannya!

Output akan terlihat seperti:
```
🚀 Using GPU: GeForce GT 1030
   VRAM Available: 2.0 GB
```

### Option B: Training dengan DeepSpeed (Rekomendasi untuk GT 1030)

```powershell
python train.py --epochs 5 --batch 4 --config tiny --deepspeed --deepspeed_config deepspeed_config.json
```

**Catatan:** DeepSpeed config sudah dioptimasi untuk GT 1030 dengan:
- Mixed precision (FP16) untuk menghemat VRAM
- Gradient accumulation untuk batch size lebih besar tanpa OOM
- ZeRO-2 optimization

### Option C: Larger Model dengan GPU

```powershell
# Untuk config '3b' (150M params, not true 3B)
python train.py --epochs 3 --batch 4 --config 3b --deepspeed
```

## Troubleshooting

### 1. "CUDA out of memory" Error

Kurangi batch size:
```powershell
python train.py --batch 2 --epochs 5
```

Atau gunakan gradient accumulation:
```powershell
python train.py --batch 2 --accum-steps 4 --epochs 5
```

### 2. "CUDA not found" atau "No module named 'torch'"

Reinstall PyTorch dengan CUDA:
```powershell
pip uninstall torch -y
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### 3. "DeepSpeed initialization failed"

Install DeepSpeed:
```powershell
pip install deepspeed==0.10.0
```

Atau training tanpa DeepSpeed (tanpa flag `--deepspeed`):
```powershell
python train.py --epochs 5 --batch 4
```

### 4. Cek CUDA Memory Usage

```powershell
nvidia-smi
```

### 5. Optimize VRAM Usage

Nonaktifkan activation checkpointing atau gunakan CPU checkpointing jika perlu:

Edit `deepspeed_config.json`:
```json
"activation_checkpointing": {
  "cpu_checkpointing": true
}
```

## Performance Tips

1. **Gunakan FP16 (Mixed Precision):** Lebih cepat + hemat VRAM
2. **Gradient Accumulation:** Simulasi batch size lebih besar tanpa OOM
3. **Smaller Sequence Length:** Gunakan `--seq-len 32` atau `64` saja
4. **Fewer Experts:** Untuk tiny config, gunakan `--config tiny` (4 experts vs 16)

## Contoh Command yang Direkomendasikan untuk GT 1030

```powershell
# Untuk training cepat dan stabil:
python train.py `
  --config tiny `
  --epochs 10 `
  --batch 8 `
  --seq-len 64 `
  --deepspeed `
  --input examples/sample_text.txt

# Atau dengan gradient accumulation:
python train.py `
  --config tiny `
  --epochs 5 `
  --batch 2 `
  --accum-steps 4 `
  --seq-len 64 `
  --deepspeed
```

## Monitoring Training

Buat file `monitor_gpu.py` untuk monitor GPU usage real-time:

```python
import subprocess
import time

while True:
    result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total,utilization.gpu', '--format=csv,noheader'], 
                          capture_output=True, text=True)
    print(f"[{time.strftime('%H:%M:%S')}] {result.stdout.strip()}")
    time.sleep(2)
```

Jalankan di terminal terpisah:
```powershell
python monitor_gpu.py
```

## Referensi

- NVIDIA CUDA Docs: https://docs.nvidia.com/cuda/
- PyTorch GPU: https://pytorch.org/docs/stable/notes/cuda.html
- DeepSpeed: https://www.deepspeed.ai/
- GT 1030 Specs: https://www.nvidia.com/en-us/geforce/gaming-laptops/geforce-gt-1030/

---

**Last Updated:** Dec 28, 2025  
**Tested on:** Windows 11, NVIDIA GT 1030, CUDA 12.1, PyTorch 2.0+
