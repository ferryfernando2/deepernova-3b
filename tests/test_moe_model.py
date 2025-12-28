import torch
from src.moe_layer import SimpleMoE
from src.model import MoETransformer


def test_moe_layer_shapes():
    moe = SimpleMoE(d_model=16, d_ff=32, num_experts=4)
    x = torch.randn(4, 2, 16)
    out, aux = moe(x)
    assert out.shape == x.shape
    assert aux.shape == torch.tensor(0.).shape or isinstance(aux, torch.Tensor)


def test_transformer_forward():
    cfg = {'vocab_size': 50, 'd_model': 32, 'n_layers': 2, 'n_heads': 4, 'd_ff': 64, 'num_experts': 2}
    model = MoETransformer(**cfg)
    ids = torch.randint(0, 50, (2, 8))
    logits, aux = model(ids)
    assert logits.shape[0] == 2
    assert logits.shape[1] == 8
    assert logits.shape[2] == 50
    assert isinstance(aux, torch.Tensor)
