import torch
from src.moe_layer import SimpleMoE


def test_moe_top2_shapes():
    moe = SimpleMoE(d_model=16, d_ff=32, num_experts=4, top_k=2)
    x = torch.randn(4, 2, 16)
    out, aux = moe(x)
    assert out.shape == x.shape
    assert isinstance(aux, torch.Tensor)
