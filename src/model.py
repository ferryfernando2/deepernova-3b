import torch
import torch.nn as nn
from src.moe_layer import SimpleMoE

class TransformerBlock(nn.Module):
    def __init__(self, d_model, n_heads, d_ff=None, use_moe=False, num_experts=8, moe_top_k=1):
        super().__init__()
        self.attn = nn.MultiheadAttention(d_model, n_heads)
        self.ln1 = nn.LayerNorm(d_model)
        self.ln2 = nn.LayerNorm(d_model)
        self.use_moe = use_moe
        if use_moe:
            assert d_ff is not None
            self.moe = SimpleMoE(d_model, d_ff, num_experts=num_experts, top_k=moe_top_k)
        else:
            self.ff = nn.Sequential(nn.Linear(d_model, d_ff), nn.ReLU(), nn.Linear(d_ff, d_model))

    def forward(self, x, attn_mask=None):
        # x: (seq_len, batch, d_model)
        res = x
        x2, _ = self.attn(x, x, x, attn_mask=attn_mask)
        x = self.ln1(res + x2)
        res = x
        if self.use_moe:
            x2, load_loss = self.moe(x)
        else:
            x2 = self.ff(x)
            load_loss = x2.new_tensor(0.0)
        x = self.ln2(res + x2)
        return x, load_loss

class MoETransformer(nn.Module):
    def __init__(self, vocab_size, d_model=1024, n_layers=22, n_heads=16, d_ff=4096, num_experts=16, moe_layers=None, moe_top_k=1):
        super().__init__()
        self.tok_emb = nn.Embedding(vocab_size, d_model)
        self.pos_emb = nn.Parameter(torch.zeros(1, 1024, d_model))  # max len 1024
        self.layers = nn.ModuleList()
        if moe_layers is None:
            moe_layers = list(range(n_layers))  # use MoE in all layers by default
        for i in range(n_layers):
            use_moe = (i in moe_layers)
            self.layers.append(TransformerBlock(d_model, n_heads, d_ff=d_ff, use_moe=use_moe, num_experts=num_experts, moe_top_k=moe_top_k))
        self.ln = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size, bias=False)

    def forward(self, ids):
        # ids: (batch, seq_len)
        ids = ids.t()  # (seq_len, batch)
        seq_len, batch = ids.shape
        # pos_emb is shaped (1, max_len, d); slice and reshape to (seq_len, 1, d) so it broadcasts over batch
        x = self.tok_emb(ids) + self.pos_emb[0, :seq_len, :].unsqueeze(1)
        total_aux = x.new_tensor(0.0)
        for l in self.layers:
            x, aux = l(x)
            total_aux = total_aux + aux
        x = self.ln(x)
        logits = self.head(x)  # (seq_len, batch, vocab)
        logits = logits.permute(1, 0, 2)  # (batch, seq_len, vocab)
        return logits, total_aux


def count_parameters(model):
    return sum(p.numel() for p in model.parameters())
