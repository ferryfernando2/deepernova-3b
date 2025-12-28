#!/usr/bin/env python3
"""
Training script yang auto-detect GPU/CPU.
Support dataset besar dengan streaming.
"""

import argparse
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
import json
from src.model import MoETransformer, count_parameters
from src.tokenizer import SimpleTokenizer
from tqdm import tqdm
import os
import time

class TokenDataset(Dataset):
    def __init__(self, texts, tokenizer, seq_len=128):
        self.examples = []
        for text in texts:
            ids = tokenizer.encode(text)
            if len(ids) <= 1:
                continue
            # Create overlapping windows for better training
            for i in range(0, max(1, len(ids) - 1), seq_len // 2):
                chunk = ids[i:i+seq_len]
                if len(chunk) < 2:
                    continue
                self.examples.append(chunk)

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        x = self.examples[idx]
        return torch.tensor(x, dtype=torch.long)

def collate_fn(batch):
    maxlen = max(len(x) for x in batch)
    out = torch.full((len(batch), maxlen), 0, dtype=torch.long)
    for i, x in enumerate(batch):
        out[i, :len(x)] = x
    return out

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='examples/sample_text.txt')
    parser.add_argument('--tokenizer', default='data/tokenizer.json')
    parser.add_argument('--epochs', type=int, default=1)
    parser.add_argument('--batch', type=int, default=2)
    parser.add_argument('--seq-len', type=int, default=128)
    parser.add_argument('--config', choices=['tiny', 'default', '3b'], default='tiny')
    parser.add_argument('--save-dir', default='checkpoints')
    parser.add_argument('--save-every', type=int, default=1)
    args = parser.parse_args()

    # Load tokenizer
    print('[*] Loading tokenizer...')
    with open(args.tokenizer, 'r', encoding='utf-8') as f:
        tok_data = json.load(f)
    tok = SimpleTokenizer()
    tok.vocab = tok_data['vocab']
    tok.inv_vocab = {int(v): k for k, v in tok.vocab.items()}
    print(f'[✓] Vocab size: {len(tok.vocab)}')

    # Load data
    print('[*] Loading dataset...')
    texts = [l.strip() for l in open(args.input, 'r', encoding='utf-8', errors='ignore') if l.strip()]
    print(f'[✓] Loaded {len(texts):,} lines')
    
    # Create dataset
    print('[*] Preparing dataset...')
    ds = TokenDataset(texts[:min(len(texts), 1000000)], tok, seq_len=args.seq_len)  # Cap at 1M samples
    dl = DataLoader(ds, batch_size=args.batch, shuffle=True, collate_fn=collate_fn, num_workers=0)
    print(f'[✓] {len(ds):,} training examples')

    # Model config
    if args.config == 'tiny':
        cfg = {'vocab_size': len(tok.vocab), 'd_model': 128, 'n_layers': 2, 'n_heads': 4, 'd_ff': 256, 'num_experts': 4, 'moe_top_k': 1}
    elif args.config == '3b':
        cfg = {'vocab_size': len(tok.vocab), 'd_model': 512, 'n_layers': 16, 'n_heads': 8, 'd_ff': 2048, 'num_experts': 8, 'moe_top_k': 1}
    else:
        cfg = {'vocab_size': len(tok.vocab), 'd_model': 256, 'n_layers': 8, 'n_heads': 8, 'd_ff': 1024, 'num_experts': 8, 'moe_top_k': 1}

    # Create model
    print('[*] Creating model...')
    model = MoETransformer(**cfg)
    print(f'[✓] {count_parameters(model) / 1e6:.1f}M parameters')

    # Device
    if torch.cuda.is_available():
        device = torch.device('cuda')
        print(f'[✓] 🎮 GPU: {torch.cuda.get_device_name(0)}')
        print(f'    Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')
    else:
        device = torch.device('cpu')
        print(f'[⚠️] CPU mode (slower)')
    
    model.to(device)

    # Training
    opt = torch.optim.AdamW(model.parameters(), lr=1e-4)
    ce = nn.CrossEntropyLoss(ignore_index=0)
    
    model.train()
    
    print(f'\n{"="*60}')
    print(f'Starting training: {args.epochs} epochs, batch={args.batch}')
    print(f'{"="*60}\n')
    
    global_step = 0
    for ep in range(args.epochs):
        pbar = tqdm(dl, desc=f'Epoch {ep+1}/{args.epochs}', unit='batch')
        epoch_loss = 0
        
        for batch_idx, batch in enumerate(pbar):
            batch = batch.to(device)
            
            # Forward
            inputs = batch[:, :-1]
            targets = batch[:, 1:]
            
            logits, load_loss = model(inputs)
            
            # Loss
            loss = ce(logits.reshape(-1, len(tok.vocab)), targets.reshape(-1))
            loss = loss + 0.01 * load_loss
            
            # Backward
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            
            epoch_loss += loss.item()
            global_step += 1
            
            # Progress
            avg_loss = epoch_loss / (batch_idx + 1)
            pbar.set_postfix({'loss': f'{avg_loss:.4f}'})
        
        # Save
        if (ep + 1) % args.save_every == 0:
            os.makedirs(args.save_dir, exist_ok=True)
            ckpt_path = f'{args.save_dir}/model_epoch{ep+1}.pt'
            torch.save(model.state_dict(), ckpt_path)
            size_mb = os.path.getsize(ckpt_path) / 1024 / 1024
            print(f'\n[✓] Checkpoint: {ckpt_path} ({size_mb:.1f}MB)')
    
    print(f'\n{"="*60}')
    print(f'✅ Training complete!')
    print(f'{"="*60}')
