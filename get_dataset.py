#!/usr/bin/env python3
"""
Download dan prepare datasets untuk training MoE model.
"""

import os
import requests
import json
from pathlib import Path

def download_file(url, filename, chunk_size=8192):
    """Download file dengan progress bar."""
    print(f"[*] Downloading: {filename}")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filename, 'wb') as f:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"    {percent:.1f}% ({downloaded}/{total_size} bytes)", end='\r')
    
    if total_size > 0:
        print(f"    100.0% ({total_size} bytes) ✓")
    else:
        print(f"    Downloaded ✓")

def main():
    print("\n" + "="*70)
    print("Dataset Collection for MoE Training")
    print("="*70 + "\n")
    
    output_file = 'examples/sample_text.txt'
    examples_dir = Path('examples')
    examples_dir.mkdir(exist_ok=True)
    
    # Check existing file
    existing_lines = 0
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_lines = len([l for l in f if l.strip()])
        print(f"[*] Existing data: {existing_lines} lines")
    
    print("\n" + "="*70)
    print("AVAILABLE DATASETS")
    print("="*70 + "\n")
    
    datasets = {
        "1": {
            "name": "Indonesian Wikipedia (WikiText-103-v1)",
            "desc": "High-quality Indonesian text (10,000+ lines)",
            "url": "https://raw.githubusercontent.com/facebookresearch/FAIR_wiki_corpus/master/indonesian/wiki.txt",
            "type": "wikipedia"
        },
        "2": {
            "name": "Common Crawl Indonesian",
            "desc": "Web-crawled Indonesian text (5,000+ lines)",
            "url": "https://dumps.wikimedia.org/idwiki/latest/idwiki-latest-pages-articles.xml.bz2",
            "type": "web"
        },
        "3": {
            "name": "Indonesian News Articles (Sample)",
            "desc": "Curated news articles in Indonesian (3,000+ lines)",
            "url": "https://raw.githubusercontent.com/zaferbas/Indonesian-News-from-Detik/master/news.txt",
            "type": "news"
        },
        "4": {
            "name": "Generated Synthetic Data",
            "desc": "Create synthetic training data locally (5,000+ lines)",
            "url": None,
            "type": "synthetic"
        },
        "5": {
            "name": "Use Local File",
            "desc": "Load from your own .txt file",
            "url": None,
            "type": "local"
        }
    }
    
    for key, ds in datasets.items():
        print(f"{key}. {ds['name']}")
        print(f"   └─ {ds['desc']}")
        if ds['url']:
            print(f"   └─ Source: {ds['url'][:60]}...")
        print()
    
    choice = input("Pilih dataset (1-5) atau 'a' untuk semua: ").strip().lower()
    
    if choice == 'a':
        choices = list(datasets.keys())
    else:
        choices = [choice] if choice in datasets else []
    
    if not choices:
        print("❌ Pilihan tidak valid!")
        return
    
    all_text = []
    
    # Load existing data
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            all_text = [l.strip() for l in f if l.strip()]
    
    print(f"\n{'='*70}")
    print("DOWNLOADING & PROCESSING")
    print(f"{'='*70}\n")
    
    for choice in choices:
        if choice not in datasets:
            continue
        
        ds = datasets[choice]
        print(f"\n[*] Processing: {ds['name']}")
        print("-" * 70)
        
        if choice == "1":  # Wikipedia
            try:
                print("📥 Downloading Indonesian Wikipedia text...")
                response = requests.get(ds['url'], timeout=30)
                if response.status_code == 200:
                    lines = response.text.split('\n')
                    valid_lines = [l.strip() for l in lines if len(l.strip()) > 20]
                    print(f"   ✓ Got {len(valid_lines)} lines")
                    all_text.extend(valid_lines)
                else:
                    print(f"   ❌ Failed (Status: {response.status_code})")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        elif choice == "2":  # Common Crawl
            print("📥 Downloading Common Crawl Indonesian Wikipedia...")
            try:
                response = requests.get(ds['url'], timeout=60)
                if response.status_code == 200:
                    # Simple text extraction from Wikipedia dump
                    lines = response.text.split('\n')
                    valid_lines = [l.strip() for l in lines if l.strip() and len(l) > 30][:5000]
                    print(f"   ✓ Extracted {len(valid_lines)} lines")
                    all_text.extend(valid_lines)
                else:
                    print(f"   ❌ Failed (Status: {response.status_code})")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        elif choice == "3":  # News
            print("📥 Downloading Indonesian news data...")
            try:
                response = requests.get(ds['url'], timeout=30)
                if response.status_code == 200:
                    lines = response.text.split('\n')
                    valid_lines = [l.strip() for l in lines if len(l.strip()) > 20]
                    print(f"   ✓ Got {len(valid_lines)} lines")
                    all_text.extend(valid_lines)
                else:
                    print(f"   ❌ Failed (Status: {response.status_code})")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        elif choice == "4":  # Synthetic
            print("🔄 Generating synthetic training data...")
            synthetic = generate_synthetic_data(5000)
            all_text.extend(synthetic)
            print(f"   ✓ Generated {len(synthetic)} lines")
        
        elif choice == "5":  # Local file
            filepath = input("   Masukkan path file .txt: ").strip().strip('"')
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = [l.strip() for l in f if l.strip()]
                print(f"   ✓ Loaded {len(lines)} lines")
                all_text.extend(lines)
            else:
                print(f"   ❌ File tidak ditemukan: {filepath}")
    
    # Remove duplicates
    print(f"\n[*] Removing duplicates...")
    all_text = list(dict.fromkeys(all_text))  # Preserve order, remove duplicates
    print(f"   ✓ {len(all_text)} unique lines")
    
    # Save
    print(f"\n[*] Saving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in all_text:
            f.write(line + '\n')
    
    print(f"   ✓ Saved {len(all_text)} lines")
    
    print(f"\n{'='*70}")
    print("✅ DATASET READY FOR TRAINING")
    print(f"{'='*70}")
    print(f"""
📊 Stats:
   - File: {output_file}
   - Lines: {len(all_text):,}
   - Size: {os.path.getsize(output_file) / 1024 / 1024:.1f} MB

🚀 Next step - Train:
   python train.py --epochs 20 --batch 2 --config tiny --seq-len 128
   
   atau untuk lebih besar:
   python train.py --epochs 10 --batch 1 --config default
""")

def generate_synthetic_data(count=5000):
    """Generate synthetic training data."""
    topics = [
        "Kecerdasan buatan", "Machine learning", "Deep learning", "Neural networks",
        "Python programming", "Data science", "Natural language processing",
        "Computer vision", "Reinforcement learning", "Transfer learning",
        "Cloud computing", "Docker", "Kubernetes", "DevOps", "Microservices",
        "REST API", "GraphQL", "Database", "SQL", "NoSQL", "MongoDB", "PostgreSQL",
        "Web development", "Frontend", "Backend", "React", "Vue.js", "Node.js",
        "JavaScript", "TypeScript", "HTML", "CSS", "Framework", "Library",
        "Git", "GitHub", "Version control", "Agile", "Scrum", "CI/CD",
        "Testing", "Unit test", "Integration test", "Security", "Encryption",
        "Authentication", "Authorization", "API Gateway", "Load balancer",
        "Cache", "Redis", "Message queue", "Kafka", "Event streaming",
        "Blockchain", "Cryptocurrency", "Smart contracts", "IoT", "Edge computing",
        "Mobile app", "Android", "iOS", "Flutter", "React Native", "Game development",
        "3D graphics", "WebGL", "AR/VR", "Metaverse", "AI ethics", "Bias",
        "Fairness", "Explainability", "Model interpretability", "Production ML"
    ]
    
    actions = [
        "adalah teknologi yang", "adalah konsep penting dalam", "membantu dalam",
        "digunakan untuk", "berfungsi sebagai", "merupakan bagian dari",
        "mempercepat proses", "meningkatkan efisiensi", "mengurangi biaya",
        "memudahkan pekerjaan", "mengotomatisasi", "mengintegrasikan"
    ]
    
    results = [
        "pengembangan aplikasi modern.", "implementasi sistem yang scalable.",
        "peningkatan performa dan kecepatan.", "optimasi resource dan memory.",
        "keamanan data dan privacy pengguna.", "user experience yang lebih baik.",
        "kolaborasi tim yang efektif.", "inovasi dalam industri teknologi.",
        "solusi bisnis yang powerful.", "transformasi digital perusahaan.",
        "efisiensi operasional yang tinggi.", "pengalaman pengguna yang seamless."
    ]
    
    import random
    data = []
    for _ in range(count):
        topic = random.choice(topics)
        action = random.choice(actions)
        result = random.choice(results)
        sentence = f"{topic} {action} {result}"
        data.append(sentence)
    
    return data

if __name__ == '__main__':
    main()
