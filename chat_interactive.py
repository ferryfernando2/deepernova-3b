#!/usr/bin/env python3
"""Interactive chat with MoE model - simple and user-friendly."""

import sys
sys.path.insert(0, '.')

import torch
from src.model import MoETransformer
from src.tokenizer import SimpleTokenizer
import torch.nn.functional as F

def generate(model, tokenizer, prompt, max_len=50, temperature=0.8, top_k=15, device='cpu'):
    """Generate text from prompt."""
    model.eval()
    
    ids = tokenizer.encode(prompt)
    ids = torch.tensor([ids], dtype=torch.long, device=device)
    
    with torch.no_grad():
        for _ in range(max_len):
            logits, _ = model(ids)
            logits = logits[0, -1, :] / temperature
            probs = F.softmax(logits, dim=-1)
            
            if top_k > 0:
                top_probs, top_indices = torch.topk(probs, min(top_k, len(probs)))
                next_idx = top_indices[torch.multinomial(top_probs, 1)]
            else:
                next_idx = torch.argmax(logits, dim=-1, keepdim=True)
            
            ids = torch.cat([ids, next_idx.unsqueeze(0)], dim=1)
            
            # Stop if <eos>
            eos_id = tokenizer.vocab.get('<eos>', -1)
            if next_idx.item() == eos_id:
                break
    
    return tokenizer.decode(ids[0].tolist())

def main():
    # Config - tiny model
    config = {
        'd_model': 128,
        'n_layers': 2,
        'n_heads': 4,
        'd_ff': 256,
        'num_experts': 4,
        'moe_top_k': 1
    }
    
    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n{'='*60}")
    print(f"MoE AI Chat - Interactive")
    print(f"{'='*60}")
    print(f"Device: {device}")
    
    # Load tokenizer
    print("\n[*] Loading tokenizer...")
    tokenizer = SimpleTokenizer()
    tokenizer.load('data/tokenizer.json')
    print(f"[✓] Vocab size: {len(tokenizer.vocab)}")
    
    # Create model
    print("[*] Creating model...")
    model = MoETransformer(
        vocab_size=len(tokenizer.vocab),
        **config
    ).to(device)
    print(f"[✓] Model: {sum(p.numel() for p in model.parameters()) / 1e6:.1f}M params")
    
    # Load checkpoint
    print("[*] Loading checkpoint...")
    try:
        checkpoint = torch.load('checkpoints/model_epoch5.pt', map_location=device)
        model.load_state_dict(checkpoint, strict=False)
        print(f"[✓] Loaded: model_epoch5.pt")
    except FileNotFoundError:
        print(f"[!] model_epoch5.pt not found, trying model_epoch2.pt...")
        checkpoint = torch.load('checkpoints/model_epoch2.pt', map_location=device)
        model.load_state_dict(checkpoint, strict=False)
        print(f"[✓] Loaded: model_epoch2.pt")
    
    print(f"\n{'='*60}")
    print("Chat Started! Type 'quit' or 'exit' to stop.")
    print(f"{'='*60}\n")
    
    # Interactive chat loop
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! 👋")
                break
            
            # Generate response
            response = generate(
                model, tokenizer, user_input,
                max_len=50, temperature=0.7, top_k=15, device=device
            )
            
            # Clean output
            response = response.replace('<eos>', '').replace('<unk>', '?').strip()
            print(f"AI:  {response}\n")
        
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye! 👋")
            break
        except Exception as e:
            print(f"[Error] {e}\n")

if __name__ == '__main__':
    main()
