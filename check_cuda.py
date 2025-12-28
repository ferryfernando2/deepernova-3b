#!/usr/bin/env python3
"""Check CUDA setup."""

import sys
print("\n" + "="*50)
print("CUDA SETUP CHECK")
print("="*50)

try:
    import torch
    print(f"✅ PyTorch: {torch.__version__}")
    print(f"✅ CUDA Available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"✅ CUDA Version: {torch.version.cuda}")
        print(f"✅ Device: {torch.cuda.get_device_name(0)}")
        props = torch.cuda.get_device_properties(0)
        print(f"✅ Memory: {props.total_memory / 1e9:.1f} GB")
        print(f"✅ Compute Capability: {props.major}.{props.minor}")
    else:
        print("❌ CUDA not available - will use CPU")
        print("\n🔧 To enable CUDA:")
        print("   1. Make sure NVIDIA driver is installed (check nvidia-smi)")
        print("   2. Run: pip install torch --index-url https://download.pytorch.org/whl/cu121")
except Exception as e:
    print(f"❌ Error: {e}")
    print("Try reinstalling PyTorch")

print("="*50 + "\n")
