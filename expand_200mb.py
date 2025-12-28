import os, random

output = 'examples/sample_text.txt'
target = 200 * 1024 * 1024

# Load
texts = []
if os.path.exists(output):
    with open(output, 'r', encoding='utf-8', errors='ignore') as f:
        texts = [l.strip() for l in f if l.strip()]

print(f'Loaded {len(texts)} lines')

# Generate to target
size = os.path.getsize(output) if os.path.exists(output) else 0
print(f'Current: {size/1024/1024:.1f}MB / 200MB')

variations = [
    'Research indicates that ',
    'Studies show that ',
    'Evidence suggests ',
    'According to experts, ',
    'The concept of ',
    'Understanding ',
    'Recent findings reveal ',
    'Scientists discovered ',
    'Data demonstrates ',
    'Analysis shows ',
]

count = 0
while size < target and count < 1000000:
    if texts:
        base = random.choice(texts)
        prefix = random.choice(variations)
        new_text = prefix + base[:100]
        texts.append(new_text)
        size += len(new_text.encode('utf-8'))
        count += 1
    
    if count % 50000 == 0:
        progress = (size / target) * 100
        with open(output, 'w', encoding='utf-8') as f:
            for t in texts:
                f.write(t + '\n')
        print(f'Generated {count}: {progress:.1f}% complete')

# Final save
with open(output, 'w', encoding='utf-8') as f:
    for t in texts:
        f.write(t + '\n')

final_size = os.path.getsize(output) / 1024 / 1024
print(f'DONE! Size: {final_size:.1f}MB, Lines: {len(texts)}')
