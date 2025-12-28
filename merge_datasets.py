#!/usr/bin/env python3
"""
Merge journals_corpus.txt dengan examples/sample_text.txt
dan prepare for large-scale training.
"""

import os
from pathlib import Path

def merge_datasets():
    """Merge journal corpus dengan existing sample data."""
    journal_file = Path('data/journals_corpus.txt')
    sample_file = Path('examples/sample_text.txt')
    output_file = Path('examples/training_corpus_combined.txt')
    
    if not journal_file.exists():
        print(f"[!] {journal_file} tidak ditemukan. Skip merge.")
        return
    
    print(f"[*] Merging datasets...")
    
    # Read both files
    print(f"  Reading {sample_file}...")
    with open(sample_file, 'r', encoding='utf-8') as f:
        sample_lines = [l.strip() for l in f if l.strip()]
    print(f"    -> {len(sample_lines)} lines")
    
    print(f"  Reading {journal_file}...")
    with open(journal_file, 'r', encoding='utf-8') as f:
        journal_lines = [l.strip() for l in f if l.strip()]
    print(f"    -> {len(journal_lines)} lines")
    
    # Combine and deduplicate
    print(f"  Deduplicating...")
    all_lines = list(dict.fromkeys(sample_lines + journal_lines))
    print(f"    -> {len(all_lines)} unique lines")
    
    # Write combined
    print(f"  Writing to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in all_lines:
            f.write(line + '\n')
    
    combined_size = output_file.stat().st_size / 1024 / 1024
    print(f"    -> {combined_size:.1f} MB")
    
    print(f"\n✅ Merge complete!")
    print(f"   Output: {output_file}")
    print(f"   Ready for training:")
    print(f"   python train.py --config default --epochs 20 --batch 2 --input {output_file}")

if __name__ == '__main__':
    merge_datasets()
