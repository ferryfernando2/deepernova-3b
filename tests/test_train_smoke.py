import torch
from src.tokenizer import SimpleTokenizer
from src.model import MoETransformer


def test_one_training_step():
    texts = ["hello world", "another line for test"]
    tok = SimpleTokenizer()
    tok.build_vocab(texts, vocab_size=20)
    ds = []
    for t in texts:
        ids = tok.encode(t)
        ds.append(ids)
    # simple batch of two
    maxlen = max(len(x) for x in ds)
    batch = torch.zeros((2, maxlen), dtype=torch.long)
    for i, x in enumerate(ds):
        batch[i, :len(x)] = torch.tensor(x, dtype=torch.long)

    cfg = {'vocab_size': len(tok.vocab), 'd_model': 32, 'n_layers': 1, 'n_heads': 4, 'd_ff': 64, 'num_experts': 2}
    model = MoETransformer(**cfg)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-4)
    model.train()
    inputs = batch[:, :-1]
    targets = batch[:, 1:]
    logits, aux = model(inputs)
    logits = logits.reshape(-1, logits.size(-1))
    targets = targets.reshape(-1)
    loss = torch.nn.functional.cross_entropy(logits, targets, ignore_index=0) + 1e-2 * aux
    loss.backward()
    opt.step()
    assert loss.item() >= 0
