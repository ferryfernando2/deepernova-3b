#!/usr/bin/env python3
"""Test chat dengan beberapa prompt."""

import sys
sys.path.insert(0, '.')
import torch
from src.model import MoETransformer
from src.tokenizer import SimpleTokenizer
import torch.nn.functional as F

# Load
tokenizer = SimpleTokenizer()
tokenizer.load('data/tokenizer.json')
model = MoETransformer(vocab_size=5000, d_model=128, n_layers=2, n_heads=4, d_ff=256, num_experts=4, moe_top_k=1)
model.load_state_dict(torch.load('checkpoints/model_epoch5.pt', map_location='cpu'), strict=False)
model.eval()

print('\n' + '='*60)
print('MoE Chat Test - Batch Queries')
print('='*60 + '\n')

queries = [
    'hello world',
    'machine learning adalah',
    'artificial intelligence',
    'deep learning',
    'python programming',
]

def generate(prompt, max_len=30, temp=0.7, top_k=10):
    ids = torch.tensor([tokenizer.encode(prompt)], dtype=torch.long)
    with torch.no_grad():
        for _ in range(max_len):
            logits, _ = model(ids)
            logits = logits[0, -1, :] / temp
            probs = torch.softmax(logits, dim=-1)
            if top_k > 0:
                top_probs, top_indices = torch.topk(probs, min(top_k, len(probs)))
                next_idx = top_indices[torch.multinomial(top_probs, 1)]
            else:
                next_idx = torch.argmax(logits, dim=-1, keepdim=True)
            ids = torch.cat([ids, next_idx.unsqueeze(0)], dim=1)
    return tokenizer.decode(ids[0].tolist()).replace('<eos>', '').replace('<unk>', '?').strip()

for q in queries:
    resp = generate(q)
    print(f'Q: {q}')
    print(f'A: {resp}\n')

print('='*60)
print('Test Complete!')
print('='*60)
