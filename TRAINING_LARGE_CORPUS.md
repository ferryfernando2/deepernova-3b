# 🚀 Training with Large Journal Corpus (700MB)

## Status
- Download journals dari PubMed Central OA: **RUNNING** (background)
- Target size: **700 MB**
- Output file: `data/journals_corpus.txt`

---

## 📊 Next Steps (Setelah Download Selesai)

### 1. Merge Dataset
Gabungkan journal corpus dengan existing data:
```powershell
# Append journals ke training data
Get-Content data/journals_corpus.txt | Add-Content examples/sample_text.txt
```

### 2. Check Combined Size
```powershell
$size = (Get-Item examples/sample_text.txt).Length / 1MB
$lines = (Get-Content examples/sample_text.txt | Measure-Object -Line).Lines
Write-Host "Combined dataset: $lines lines, $([math]::Round($size, 1)) MB"
```

### 3. Train dengan Config Besar (RECOMMENDED)

#### Option A: Default Model (Balanced - 1-2 jam)
```powershell
python train.py `
  --config default `
  --epochs 20 `
  --batch 2 `
  --seq-len 256 `
  --input examples/sample_text.txt
```

#### Option B: 3B Model (Lebih Besar - 3-5 jam, butuh GPU/DeepSpeed)
```powershell
python train.py `
  --config 3b `
  --epochs 10 `
  --batch 1 `
  --seq-len 512 `
  --deepspeed `
  --input examples/sample_text.txt
```

#### Option C: GPU Training (Tercepat - dengan DeepSpeed)
```powershell
python train.py `
  --config default `
  --epochs 30 `
  --batch 4 `
  --seq-len 512 `
  --deepspeed `
  --input examples/sample_text.txt
```

---

## 🔍 Monitoring Download

Check status dalam PowerShell:
```powershell
# Size saat ini
$size = (Get-Item data/journals_corpus.txt -ErrorAction SilentlyContinue).Length / 1MB
if ($size) {
    Write-Host "Downloaded: $([math]::Round($size, 1)) MB / 700 MB"
} else {
    Write-Host "Download belum mulai..."
}
```

---

## ⚙️ Training Recommendations

Dengan dataset 700MB+ dan model larger:
- **Ekspektasi kualitas:** ⭐⭐⭐⭐ (jauh lebih baik)
- **Response time:** Normal (model sudah trained baik)
- **Coherence:** Tinggi (understand context & grammar)
- **Vocabulary:** Luas (~10k+ tokens dari jurnal)

---

## 📋 Checklist Sebelum Training

- [ ] Download journals selesai (~700MB)
- [ ] Data merged ke `examples/sample_text.txt`
- [ ] Config dipilih (tiny/default/3b)
- [ ] GPU available (optional, untuk speed-up)
- [ ] Storage cukup untuk checkpoints (~2-5GB)

---

## 🎯 Success Metrics

Setelah training 20+ epochs dengan 700MB+ data:
- Loss harus drop signifikan (< 2.0)
- Chat responses jauh lebih natural
- Coherence & grammar meningkat drastis
- Bisa understand complex queries

---

## 📞 Testing After Training

```powershell
# Interactive chat dengan model baru
python chat_interactive.py
```

Expected improvement dari training dengan jurnal:
- Epoch 5: Respons random/broken
- Epoch 15: Ada pattern, tapi masih kurang natural  
- Epoch 25+: Natural language, understand context, good grammar

---

**ETA untuk download:** Tergantung bandwidth (1-6 jam untuk 700MB)  
**Total training time:** 1-5 jam (tergantung config & GPU)
