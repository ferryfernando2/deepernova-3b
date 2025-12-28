#!/usr/bin/env python3
"""Rapid 700MB+ synthetic journal generator."""
import random
from pathlib import Path

def gen():
    topics = ["AI","ML","Deep Learning","NLP","CV","IoT","Cloud","Security","Network","Database","API","Web","Mobile","Game","DevOps","Data Science","Quantum","Blockchain","Robotics","AR/VR","Healthcare IT","FinTech","EdTech","AgriTech","EnergyTech"]
    verbs = ["improves","enhances","enables","facilitates","accelerates","optimizes","automates","streamlines","transforms","revolutionizes","advances","strengthens","simplifies","amplifies"]
    domains = ["performance","efficiency","security","scalability","reliability","accessibility","sustainability","productivity","innovation","competitiveness","profitability","user experience","system integration"]
    
    output = Path('data/journals_corpus.txt')
    output.parent.mkdir(exist_ok=True)
    
    target = 700 * 1024 * 1024
    count = 0
    size = 0
    
    print("Generating 700MB synthetic journal corpus...\n")
    
    with open(output, 'w', encoding='utf-8') as f:
        while size < target:
            t, v, d = random.choice(topics), random.choice(verbs), random.choice(domains)
            line = f"{t} {v} {d} in modern systems through advanced implementation strategies and best practices."
            f.write(line + '\n')
            size += len(line.encode('utf-8')) + 1
            count += 1
            if count % 100000 == 0:
                mb = size / 1024 / 1024
                pct = (mb / 700) * 100
                print(f"  {count:,} lines | {mb:.1f}MB ({pct:.0f}%)")
    
    final_mb = size / 1024 / 1024
    print(f"\n✅ Done! {count:,} lines, {final_mb:.1f}MB")
    print(f"\nNext: python train.py --config default --epochs 30 --batch 2")

if __name__ == '__main__':
    gen()
