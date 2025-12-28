# 📊 Dataset Collection Guide

## Current Status
- **File:** `examples/sample_text.txt`
- **Lines:** 11,495
- **Size:** ~1.0 MB

---

## 🎯 Cara Mendapatkan Datasets

### **Opsi 1: Generate Synthetic Data (Tercepat - 30 detik)**
Buat data training artificial secara otomatis:

```powershell
python get_dataset.py
# Pilih: 4
```

✅ **Pros:**
- Cepat & tidak butuh internet
- Menghasilkan 5,000+ lines berkualitas
- Bisa di-customize

❌ **Cons:**
- Data artificial (kurang natural)
- Pattern terbatas

---

### **Opsi 2: Download dari Web (30 menit - 2 jam)**

#### a) Indonesian Wikipedia
```powershell
python get_dataset.py
# Pilih: 2
```
- 10,000+ lines berkualitas tinggi
- Format: Indonesian text dari Wikipedia

#### b) Indonesian News Articles
```powershell
python get_dataset.py
# Pilih: 3
```
- 5,000+ lines artikel berita
- Lebih natural & context-rich

---

### **Opsi 3: Upload File Sendiri (Tercepat)**
Punya file `.txt` sendiri? Gunakan itu:

```powershell
python get_dataset.py
# Pilih: 5
# Input path file: C:\Users\...\mydata.txt
```

✅ **Recommended format:**
- 1 sentence per line
- Bahasa Indonesia
- Min 20 karakter per line

---

### **Opsi 4: Manual Download dari Online Sources**

#### Popular Indonesian Datasets:

1. **Indonesian Wikipedia Dump**
   - Source: https://dumps.wikimedia.org/idwiki/
   - Format: XML
   - Size: 500MB+
   - Tool: Parsing script diperlukan

2. **Indonesian News Corpus**
   - Source: https://github.com/zaferbas/Indonesian-News-from-Detik
   - Format: JSON/TXT
   - Size: 100MB+
   - Quality: Tinggi

3. **Indonesian OSCAR Corpus** (Common Crawl)
   - Source: https://oscar-corpus.org/
   - Format: TXT
   - Size: 1GB+
   - Coverage: Web-wide

4. **Wikidata Indonesian**
   - Source: https://www.wikidata.org/
   - Format: JSON-LD
   - Quality: Sangat tinggi

5. **OpenCC Indonesian**
   - Source: https://github.com/BPaya/Indo-OpenCC
   - Format: TXT
   - Size: 50MB+

---

## 🔧 Processing Data dari Sumber Eksternal

### Step 1: Download File
```bash
# Contoh: Download Wikipedia
curl -o data.xml.bz2 https://dumps.wikimedia.org/idwiki/latest/idwiki-latest-pages-articles.xml.bz2
```

### Step 2: Extract & Prepare
```bash
# Unzip
bunzip2 data.xml.bz2

# Parse XML (gunakan tool seperti wp2txt atau similar)
# Output: text file, 1 kalimat per line
```

### Step 3: Clean Data
```powershell
# Gunakan script cleanup:
python scripts/clean_dataset.py --input data.txt --output clean_data.txt
```

### Step 4: Merge dengan Existing Data
```powershell
# Update examples/sample_text.txt dengan file baru
python get_dataset.py
# Pilih: 5
# Input: path ke clean_data.txt
```

---

## 📈 Dataset Sizes & Training Time

| Dataset Size | Training Time | Quality | Recommendation |
|---|---|---|---|
| 1K lines (0.1 MB) | 10 min | ⚠️ Poor | Tidak cukup |
| 5K lines (0.5 MB) | 30 min | ⭐ Fair | Minimum |
| 10K lines (1 MB) | 1 hour | ⭐⭐ Good | Recommended |
| 50K lines (5 MB) | 5-8 hours | ⭐⭐⭐ Great | Optimal |
| 100K+ lines (10MB+) | 12+ hours | ⭐⭐⭐⭐ Excellent | Production |

---

## 🎓 Quick Training Commands

### Dengan Dataset Saat Ini (11.5K lines):
```powershell
# Tiny model (cepat, testing)
python train.py --epochs 20 --batch 4 --config tiny --seq-len 128

# Default model (balanced)
python train.py --epochs 10 --batch 2 --config default --seq-len 256

# 3B model (lebih besar, butuh GPU)
python train.py --epochs 5 --batch 1 --config 3b --seq-len 512 --deepspeed
```

---

## 💡 Tips & Tricks

### 1. Tambah Data dengan Cepat
```powershell
# Multiple iterations
for ($i=1; $i -le 3; $i++) {
    echo "4" | python get_dataset.py
}
```

### 2. Check Data Quality
```powershell
# Lihat sample data
Get-Content examples/sample_text.txt -TotalCount 10

# Count total lines
(Get-Content examples/sample_text.txt | Measure-Object -Line).Lines
```

### 3. Backup Data
```powershell
Copy-Item examples/sample_text.txt examples/sample_text_backup.txt
```

### 4. Custom Domain Data
Kalo punya data spesifik domain (e.g., medical, legal, tech), bisa train khusus:
- Prepare dataset domain-specific
- Fine-tune model dengan data tersebut
- Hasil: Model lebih baik di domain itu

---

## 🚀 Workflow Optimal

1. **Start:** Gunakan synthetic data (5,000 lines) → Train 10 epoch
   ```powershell
   echo "4" | python get_dataset.py
   python train.py --epochs 10 --batch 2 --config tiny
   ```

2. **Test:** Cek hasil chat
   ```powershell
   python chat_interactive.py
   ```

3. **Scale:** Tambah data dari online source → Train lebih lama
   ```powershell
   # Download Wikipedia atau News
   echo "2" | python get_dataset.py
   python train.py --epochs 20 --batch 2 --config default
   ```

4. **Production:** Combine multiple sources → Train 50+ epoch
   ```powershell
   # Combine semua data → Train dengan GPU
   python train.py --epochs 30 --batch 4 --config 3b --deepspeed
   ```

---

## ❓ FAQ

**Q: Dataset mana yang terbaik untuk bahasa Indonesia?**
A: Wikipedia (best quality) → News articles (balanced) → Synthetic (fastest)

**Q: Berapa lama proses download?**
A: Synthetic (instant), News (5 min), Wikipedia (varies)

**Q: Bisa mix multiple datasets?**
A: Ya! Jalankan `get_dataset.py` multiple kali, auto merge

**Q: Dataset bahasa lain?**
A: Script support any language, tinggal ganti source URL

---

## 📞 Need Help?

- Check file structure: `ls -la examples/`
- Monitor size: `Get-Item examples/sample_text.txt | Select Length`
- Debug training: `python train.py --epochs 1 --batch 2 --config tiny`

---

**Last Updated:** Dec 28, 2025  
**Status:** ✅ Ready for training
