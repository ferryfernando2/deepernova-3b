#!/usr/bin/env python3
"""Rebuild tokenizer efficiently from large dataset (sample-based)."""

import json
import random
from collections import Counter
from src.tokenizer import SimpleTokenizer

print('[*] Loading dataset...')
with open('examples/sample_text.txt', 'r', encoding='utf-8') as f:
    all_lines = [l.strip() for l in f if l.strip() and len(l.strip()) > 10]

print(f'[*] Total lines in file: {len(all_lines):,}')

# Sample untuk vocab building (lebih efficient)
sample_size = min(100000, len(all_lines))
sample = random.sample(all_lines, sample_size)
print(f'[*] Using {sample_size:,} samples for tokenizer...')

print('[*] Building vocabulary...')
tok = SimpleTokenizer()
tok.build_vocab(sample, vocab_size=5000)

print('[*] Saving tokenizer...')
with open('data/tokenizer.json', 'w', encoding='utf-8') as f:
    json.dump({'vocab': tok.vocab}, f)

print(f'[✓] Vocab size: {len(tok.vocab)}')
print(f'[✓] Saved to data/tokenizer.json')
print(f'[✓] Ready for training with {len(all_lines):,} lines!')
