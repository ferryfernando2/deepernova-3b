#!/usr/bin/env python3
"""Merge all datasets into single sample_text.txt with deduplication."""
import os
from pathlib import Path

def merge_all():
    files = [
        'examples/sample_text.txt',
        'examples/training_corpus_combined.txt', 
        'data/journals_corpus.txt'
    ]
    
    output = 'examples/sample_text.txt'
    temp = 'examples/sample_text_temp.txt'
    
    print("Merging all datasets...\n")
    
    # Combine into temp file
    print("[*] Combining files...")
    seen = set()
    with open(temp, 'w', encoding='utf-8') as out:
        for fname in files:
            if not os.path.exists(fname):
                print(f"  Skipping {fname} (not found)")
                continue
            
            print(f"  Processing {fname}...")
            with open(fname, 'r', encoding='utf-8') as f:
                count = 0
                for line in f:
                    line = line.strip()
                    if not line or len(line) < 30:
                        continue
                    if line not in seen:
                        seen.add(line)
                        out.write(line + '\n')
                        count += 1
                print(f"    -> Added {count} unique lines")
    
    # Replace original
    os.replace(temp, output)
    
    # Stats
    size = os.path.getsize(output) / 1024 / 1024
    lines = sum(1 for _ in open(output, 'r', encoding='utf-8'))
    
    print(f"\n✅ DONE!")
    print(f"Output: {output}")
    print(f"Lines: {lines:,}")
    print(f"Size: {size:.1f} MB")
    print(f"\nNext: python train.py --config default --epochs 30 --batch 2 --seq-len 256 --input {output}")

if __name__ == '__main__':
    merge_all()
