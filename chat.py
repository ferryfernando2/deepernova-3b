#!/usr/bin/env python3
"""Interactive chat interface with MoE AI model."""

import argparse
import sys
import torch
import torch.nn.functional as F
from src.model import MoETransformer
from src.tokenizer import SimpleTokenizer


def generate(model, tokenizer, prompt, max_len=50, temperature=0.8, top_k=10, system_prompt=None):
    """Generate text autoregressively from a prompt."""
    model.eval()
    
    # Prepend system prompt if provided
    if system_prompt:
        full_prompt = system_prompt + "\n\nUser: " + prompt + "\n\nDeepErNova: "
    else:
        full_prompt = prompt
    
    # Encode prompt
    ids = tokenizer.encode(full_prompt)
    ids = torch.tensor([ids], dtype=torch.long)
    
    # Generate tokens
    with torch.no_grad():
        for _ in range(max_len):
            # Forward pass
            logits, _ = model(ids)
            
            # Get last token logits
            logits = logits[0, -1, :] / temperature
            probs = F.softmax(logits, dim=-1)
            
            # Top-k sampling
            if top_k > 0:
                top_probs, top_indices = torch.topk(probs, min(top_k, len(probs)))
                next_idx = top_indices[torch.multinomial(top_probs, 1)]
            else:
                next_idx = torch.argmax(logits, dim=-1, keepdim=True)
            
            # Append to sequence
            ids = torch.cat([ids, next_idx.unsqueeze(0)], dim=1)
            
            # Stop if end-of-sequence (if tokenizer has it)
            if tokenizer.vocab.get('<eos>', -1) == next_idx.item():
                break
    
    return tokenizer.decode(ids[0].tolist())


def load_model_and_tokenizer(checkpoint_path, tokenizer_path, config_dict):
    """Load trained model and tokenizer."""
    # Load tokenizer
    tokenizer = SimpleTokenizer()
    tokenizer.load(tokenizer_path)
    vocab_size = len(tokenizer.vocab)
    
    print(f"[INFO] Loaded tokenizer: vocab_size={vocab_size}")
    
    # Create model with tokenizer vocab size
    model = MoETransformer(
        vocab_size=vocab_size,
        d_model=config_dict['d_model'],
        n_layers=config_dict['n_layers'],
        n_heads=config_dict['n_heads'],
        d_ff=config_dict['d_ff'],
        num_experts=config_dict['num_experts'],
        moe_top_k=config_dict['moe_top_k']
    )
    
    print(f"[INFO] Created model: {sum(p.numel() for p in model.parameters()) / 1e6:.1f}M params")
    
    # Load checkpoint
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    model.load_state_dict(checkpoint, strict=False)
    model.eval()
    
    print(f"[INFO] Loaded checkpoint: {checkpoint_path}")
    
    return model, tokenizer


def main():
    parser = argparse.ArgumentParser(description='Chat with MoE AI')
    parser.add_argument('--checkpoint', default='checkpoints/model_epoch2.pt',
                        help='Path to model checkpoint')
    parser.add_argument('--tokenizer', default='data/tokenizer.json',
                        help='Path to tokenizer')
    parser.add_argument('--max-len', type=int, default=50,
                        help='Max length for generation')
    parser.add_argument('--temperature', type=float, default=0.8,
                        help='Sampling temperature')
    parser.add_argument('--top-k', type=int, default=10,
                        help='Top-k for sampling (0=argmax)')
    parser.add_argument('--config', default='3b',
                        help='Model config (tiny/default/3b)')
    
    args = parser.parse_args()
    
    # Model configs
    configs = {
        'tiny': {
            'd_model': 128,
            'n_layers': 4,
            'n_heads': 2,
            'd_ff': 512,
            'num_experts': 4,
            'moe_top_k': 1
        },
        'default': {
            'd_model': 256,
            'n_layers': 8,
            'n_heads': 4,
            'd_ff': 1024,
            'num_experts': 8,
            'moe_top_k': 1
        },
        '3b': {
            'd_model': 512,
            'n_layers': 16,
            'n_heads': 8,
            'd_ff': 2048,
            'num_experts': 8,
            'moe_top_k': 1
        }
    }
    
    config_dict = configs.get(args.config, configs['3b'])
    
    # System prompt untuk DeepErNova
    system_prompt = """You are DeepErNova, an advanced AI assistant trained with Mixture of Experts (MoE) architecture. 
You are helpful, knowledgeable, and friendly. When asked about yourself, introduce yourself as DeepErNova.
You provide clear and concise answers to questions."""
    
    # Load model and tokenizer
    print("\n" + "="*60)
    print("Loading MoE AI Model...")
    print("="*60)
    model, tokenizer = load_model_and_tokenizer(
        args.checkpoint, args.tokenizer, config_dict
    )
    
    # Interactive chat loop
    print("\n" + "="*60)
    print("Chat with MoE AI (type 'exit' or 'quit' to leave)")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\nDeepErNova: Goodbye! Thank you for chatting with me. Have a great day!")
                break
            
            # Generate response
            print("\nDeepErNova: ", end="", flush=True)
            response = generate(
                model, tokenizer, user_input,
                max_len=args.max_len,
                temperature=args.temperature,
                top_k=args.top_k,
                system_prompt=system_prompt
            )
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\n[ERROR] {e}")
            print()


if __name__ == '__main__':
    main()
