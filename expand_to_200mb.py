#!/usr/bin/env python3
"""
Expand dataset ke 200MB dengan variation dan synthetic content
"""

import os
import random

def expand_dataset(target_mb=200):
    """Expand existing dataset dengan variation."""
    
    output_file = 'examples/sample_text.txt'
    target_size = target_mb * 1024 * 1024
    
    print(f"\n{'='*70}")
    print("DATASET EXPANSION TO 200MB")
    print(f"{'='*70}\n")
    
    # Load existing
    print("[*] Loading existing dataset...")
    with open(output_file, 'r', encoding='utf-8') as f:
        original_texts = [l.strip() for l in f if l.strip()]
    
    original_size = os.path.getsize(output_file)
    print(f"    Loaded: {len(original_texts)} lines ({original_size/1024/1024:.1f}MB)")
    
    all_texts = original_texts.copy()
    
    # Expand with variations
    print("\n[*] Generating variations and expansions...")
    
    prefixes = [
        "Research shows that ",
        "Studies indicate that ",
        "Evidence suggests that ",
        "Recent findings reveal that ",
        "According to latest research, ",
        "Scientists discovered that ",
        "Experts believe that ",
        "Data demonstrates that ",
        "Analysis shows that ",
        "Investigation reveals that ",
        "The concept of ",
        "Understanding ",
        "The field of ",
        "In the domain of ",
        "Regarding ",
    ]
    
    suffixes = [
        " is crucial for modern technology.",
        " plays a vital role in AI development.",
        " significantly impacts computational efficiency.",
        " provides valuable insights for practitioners.",
        " contributes to scientific advancement.",
        " is essential for solving complex problems.",
        " represents a paradigm shift in the industry.",
        " has revolutionized the way we work.",
        " offers promising applications across sectors.",
        " enables breakthrough innovations in technology.",
        " fundamentally changes our understanding.",
        " opens new possibilities for research.",
        " transforms the landscape of modern computing.",
        " accelerates progress in AI and ML.",
        " bridges the gap between theory and practice.",
    ]
    
    # Generate expanded content
    expansion_count = 0
    current_size = original_size
    
    while current_size < target_size and expansion_count < 1000000:
        # Method 1: Paraphrase existing texts
        if random.random() < 0.5 and original_texts:
            text = random.choice(original_texts)
            prefix = random.choice(prefixes)
            new_text = prefix + text.lower()
            all_texts.append(new_text)
            current_size += len(new_text.encode('utf-8'))
        
        # Method 2: Combine texts
        elif len(original_texts) > 1:
            text1 = random.choice(original_texts)
            text2 = random.choice(original_texts)
            new_text = f"{text1} {text2}"
            all_texts.append(new_text)
            current_size += len(new_text.encode('utf-8'))
        
        # Method 3: Add suffix
        else:
            text = random.choice(original_texts)
            suffix = random.choice(suffixes)
            new_text = text + suffix
            all_texts.append(new_text)
            current_size += len(new_text.encode('utf-8'))
        
        expansion_count += 1
        
        if expansion_count % 10000 == 0:
            progress = (current_size / target_size) * 100
            print(f"    {expansion_count:,} variations ({progress:.1f}% complete)")
        
        if current_size >= target_size:
            break
    
    print(f"\n[*] Generated {expansion_count:,} variations")
    
    # Save
    print(f"\n[*] Saving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for text in all_texts:
            f.write(text + '\n')
    
    final_size = os.path.getsize(output_file) / 1024 / 1024
    final_lines = len(all_texts)
    
    print(f"    ✓ Total lines: {final_lines:,}")
    print(f"    ✓ Final size: {final_size:.1f}MB")
    
    print(f"\n{'='*70}")
    print("✅ EXPANSION COMPLETE")
    print(f"{'='*70}\n")
    
    return final_size, final_lines

if __name__ == '__main__':
    expand_dataset(target_mb=200)
