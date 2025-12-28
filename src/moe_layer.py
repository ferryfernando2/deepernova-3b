import torch
import torch.nn as nn
import torch.nn.functional as F

class SimpleMoE(nn.Module):
    """MoE layer supporting top-k routing and batched dispatch.

    - gate: linear layer producing logits over experts.
    - experts: ModuleList of small FeedForward networks.
    - supports `top_k` (1 or 2) and a simple auxiliary load-balance loss.

    Notes:
    - This is still a simple implementation focused on clarity and correctness for
      distributed training orchestration (DeepSpeed/FSDP). For production-scale
      throughput more advanced dispatch (sharded experts) or third-party libs
      should be considered.
    """

    def __init__(self, d_model, d_ff, num_experts=8, top_k=1):
        super().__init__()
        assert top_k in (1, 2), "top_k currently supports 1 or 2"
        self.num_experts = num_experts
        self.d_model = d_model
        self.top_k = top_k
        self.experts = nn.ModuleList([nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Linear(d_ff, d_model)
        ) for _ in range(num_experts)])
        self.gate = nn.Linear(d_model, num_experts)

    def forward(self, x):
        # x: (seq_len, batch, d_model)
        seq_len, batch, d = x.shape
        tokens = seq_len * batch
        x_flat = x.reshape(tokens, d)  # (tokens, d)
        logits = self.gate(x_flat)  # (tokens, num_experts)
        probs = F.softmax(logits, dim=-1)

        # Top-k routing
        if self.top_k == 1:
            topk_vals, topk_idx = probs.topk(1, dim=-1)
            topk_vals = topk_vals.squeeze(-1)  # (tokens,)
            topk_idx = topk_idx.squeeze(-1)    # (tokens,)
        else:
            topk_vals, topk_idx = probs.topk(2, dim=-1)  # (tokens, 2)

        # load-balance loss
        mean_prob = probs.mean(dim=0)  # (num_experts,)
        load_loss = (mean_prob * mean_prob).sum() * (self.num_experts)

        # Dispatch and combine (batched per-expert processing)
        out_flat = x_flat.new_zeros((tokens, d))

        if self.top_k == 1:
            # For each expert, select its tokens and process them in one call
            for e in range(self.num_experts):
                mask = (topk_idx == e)
                if mask.any():
                    selected = x_flat[mask]
                    processed = self.experts[e](selected)
                    out_flat[mask] = processed * topk_vals[mask].unsqueeze(-1)
        else:
            # top-2: gather two expert contributions per token and sum weighted outputs
            idx0 = topk_idx[:, 0]
            idx1 = topk_idx[:, 1]
            w0 = topk_vals[:, 0]
            w1 = topk_vals[:, 1]
            # process expert 0..num_experts-1 by selecting tokens for which it appears
            # either in idx0 or idx1 and accumulate weighted outputs
            for e in range(self.num_experts):
                mask0 = (idx0 == e)
                mask1 = (idx1 == e)
                any_mask = mask0 | mask1
                if any_mask.any():
                    sel = x_flat[any_mask]
                    proc = self.experts[e](sel)
                    # determine where tokens came from first/second slot to apply weights
                    w = torch.where(mask0[any_mask], w0[any_mask], w1[any_mask]).unsqueeze(-1)
                    out_flat[any_mask] += proc * w

        out = out_flat.view(seq_len, batch, d)
        return out, load_loss
