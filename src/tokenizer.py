import json
from collections import Counter
from typing import List

class SimpleTokenizer:
    """Very small, easy-to-read tokenizer.

    - Builds vocabulary from whitespace-tokenized words (lowercased).
    - Keeps top-N frequent tokens; everything else -> <unk>.
    - Adds special tokens: <pad>, <bos>, <eos>, <unk>
    """

    def __init__(self):
        self.vocab = {}
        self.inv_vocab = {}
        self.specials = ["<pad>", "<bos>", "<eos>", "<unk>"]

    def build_vocab(self, texts: List[str], vocab_size: int = 8000):
        cnt = Counter()
        for t in texts:
            for tok in t.strip().lower().split():
                cnt[tok] += 1
        most = [w for w, _ in cnt.most_common(vocab_size - len(self.specials))]
        toks = self.specials + most
        self.vocab = {t: i for i, t in enumerate(toks)}
        self.inv_vocab = {i: t for t, i in self.vocab.items()}

    def encode(self, text: str) -> List[int]:
        ids = [self.vocab.get("<bos>")]
        for tok in text.strip().lower().split():
            ids.append(self.vocab.get(tok, self.vocab.get("<unk>")))
        ids.append(self.vocab.get("<eos>"))
        return ids

    def decode(self, ids: List[int]) -> str:
        toks = [self.inv_vocab.get(i, "<unk>") for i in ids]
        # strip bos/eos
        if toks and toks[0] == "<bos>":
            toks = toks[1:]
        if toks and toks[-1] == "<eos>":
            toks = toks[:-1]
        return " ".join(toks)

    def save(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"vocab": self.vocab}, f, ensure_ascii=False)

    def load(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.vocab = data["vocab"]
        self.inv_vocab = {int(v): k for k, v in self.vocab.items()}
