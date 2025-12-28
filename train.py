import argparse
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
import json
from src.model import MoETransformer, count_parameters
from src.tokenizer import SimpleTokenizer
from tqdm import tqdm

class TokenDataset(Dataset):
    def __init__(self, texts, tokenizer, seq_len=64):
        self.examples = []
        for t in texts:
            ids = tokenizer.encode(t)
            if len(ids) <= 1:
                continue
            # split into windows
            for i in range(0, max(1, len(ids) - 1), seq_len):
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
    parser.add_argument('--batch', type=int, default=8)
    parser.add_argument('--seq-len', type=int, default=64)
    parser.add_argument('--config', choices=['tiny', 'default', '3b'], default='tiny')
    parser.add_argument('--deepspeed', action='store_true', help='Use DeepSpeed for distributed/sharded training')
    parser.add_argument('--deepspeed_config', default='deepspeed_config.json')
    parser.add_argument('--moe-top-k', type=int, default=1, choices=[1,2], help='Top-k gating in MoE (1 or 2)')
    parser.add_argument('--accum-steps', type=int, default=1, help='Gradient accumulation steps')
    parser.add_argument('--save-dir', default='checkpoints', help='Directory to save checkpoints')
    parser.add_argument('--save-every', type=int, default=1, help='Save every N epochs')
    args = parser.parse_args()

    with open(args.tokenizer, 'r', encoding='utf-8') as f:
        tok_data = json.load(f)
    tok = SimpleTokenizer(); tok.vocab = tok_data['vocab']; tok.inv_vocab = {int(v): k for k,v in tok.vocab.items()}

    texts = [l.strip() for l in open(args.input, 'r', encoding='utf-8') if l.strip()]
    ds = TokenDataset(texts, tok, seq_len=args.seq_len)
    dl = DataLoader(ds, batch_size=args.batch, shuffle=True, collate_fn=collate_fn)

    if args.config == 'tiny':
        cfg = {'vocab_size': len(tok.vocab), 'd_model': 128, 'n_layers': 2, 'n_heads': 4, 'd_ff': 256, 'num_experts': 4, 'moe_top_k': args.moe_top_k}
    elif args.config == '3b':
        # CPU-friendly medium config: ~150M params (OOM happened at 731M on CPU)
        # Real 3B model requires GPU cluster. This demonstrates MoE architecture at scale that CPU can handle.
        cfg = {'vocab_size': 5000, 'd_model': 512, 'n_layers': 16, 'n_heads': 8, 'd_ff': 2048, 'num_experts': 8, 'moe_top_k': args.moe_top_k}
    else:
        cfg = {'vocab_size': len(tok.vocab), 'd_model': 1024, 'n_layers': 22, 'n_heads': 16, 'd_ff': 4096, 'num_experts': 16, 'moe_top_k': args.moe_top_k}

    model = MoETransformer(**cfg)

    # device / distributed / DeepSpeed initialization
    # Auto-detect GPU (CUDA) or fall back to CPU
    if torch.cuda.is_available():
        device = torch.device('cuda')
        print(f'🚀 Using GPU: {torch.cuda.get_device_name(0)}')
        print(f'   VRAM Available: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')
    else:
        device = torch.device('cpu')
        print('⚠️  CUDA not available. Falling back to CPU.')
    
    model.to(device)

    print('Params:', count_parameters(model))

    opt = torch.optim.AdamW(model.parameters(), lr=1e-4)
    ce = nn.CrossEntropyLoss(ignore_index=0)

    # Optional: integrate DeepSpeed if requested
    if args.deepspeed:
        try:
            import deepspeed
            ds_engine, opt, _, _ = deepspeed.initialize(args=None, model=model, model_parameters=model.parameters(), config=args.deepspeed_config)
            model = ds_engine
            print('DeepSpeed initialized')
        except Exception as e:
            print('DeepSpeed initialization failed:', e)
            print('Proceeding without DeepSpeed')

    model.train()
    global_step = 0
    for ep in range(args.epochs):
        pbar = tqdm(dl, desc=f'Epoch {ep+1}')
        for batch in pbar:
            batch = batch.to(device)
            # inputs and targets shifted by 1
            inputs = batch[:, :-1]
            targets = batch[:, 1:]
            logits, aux = model(inputs)
            logits = logits.reshape(-1, logits.size(-1))
            targets = targets.reshape(-1)
            loss = ce(logits, targets) + 1e-2 * aux
            if args.deepspeed and hasattr(model, 'backward'):
                model.backward(loss)
                model.step()
            else:
                loss = loss / args.accum_steps
                opt.zero_grad()
                loss.backward()
                if (global_step + 1) % args.accum_steps == 0:
                    opt.step()
                global_step += 1
            pbar.set_postfix({'loss': float(loss.detach().cpu())})

        # checkpointing
        if (ep + 1) % args.save_every == 0:
            import os
            os.makedirs(args.save_dir, exist_ok=True)
            if args.deepspeed and hasattr(model, 'save_checkpoint'):
                model.save_checkpoint(args.save_dir, tag=f'epoch{ep+1}')
            else:
                torch.save(model.state_dict(), os.path.join(args.save_dir, f'model_epoch{ep+1}.pt'))

    print('Training finished (CPU/demo or distributed if DeepSpeed).')
