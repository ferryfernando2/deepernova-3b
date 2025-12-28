import argparse
from src.tokenizer import SimpleTokenizer

def read_lines(path):
    with open(path, 'r', encoding='utf-8') as f:
        return [l.strip() for l in f if l.strip()]

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--input', required=True)
    p.add_argument('--vocab-size', type=int, default=8000)
    p.add_argument('--out', default='data/tokenizer.json')
    args = p.parse_args()

    texts = read_lines(args.input)
    tok = SimpleTokenizer()
    tok.build_vocab(texts, vocab_size=args.vocab_size)
    tok.save(args.out)
    print('Tokenizer saved ->', args.out)
