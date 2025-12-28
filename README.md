# MoE small project (target ~3B params) ✅

🔧 This repo contains a minimal PyTorch implementation of a Mixture-of-Experts (MoE) Transformer and a **simple custom tokenizer**. The code is CPU-first and intended for experimentation and testing. Training a 3B-parameter model on CPU is **impractical** but the code supports a scaled-down local setup and includes a suggested config near 3B parameters for when you have GPUs or a cluster.

## Files
- `src/model.py` - Transformer + option to use MoE in feed-forward layers
- `src/moe_layer.py` - Simple Top-1 gating MoE layer + auxiliary load-balance loss
- `src/tokenizer.py` - `SimpleTokenizer`: builds vocab from text (word-level + fallback)
- `src/data_prep.py` - Example dataset/tokenizer builder
- `train.py` - Minimal training loop (CPU-friendly) with config switch
- `scripts/compute_params.py` - helper to compute total parameters for configs

---

## Quick start (CPU, tiny test)
1. Install Python 3.10+ and create a virtualenv, then install requirements:
   - `python -m venv .venv && .\.venv\Scripts\activate && pip install -r requirements.txt`
2. Prepare data and tokenizer:
   - `python src/data_prep.py --input examples/sample_text.txt --vocab-size 8000 --out data/tokenizer.json`
3. Train a tiny model for a few steps (verify everything runs on CPU):
   - `python train.py --config tiny --tokenizer data/tokenizer.json --input examples/sample_text.txt --epochs 1 --batch 2`

### Run scripts (Windows)
- `run_train.bat` — runs tokenizer build + a tiny training run (CPU).
- `run_tests.bat` — runs the unit tests using `pytest`

**Note:** I could not run training here because Python is not available in this environment; follow the commands above locally and let me know any failures and I will help debug.  

## Notes & caveats ⚠️
- The `default` config is for small local tests. The `3b` config in `scripts/compute_params.py` suggests a combination of depth/dim/expert count approximating 3B total params — **do not try to train that on CPU**; use GPUs / cluster / model-sharding.
- The MoE here uses a simple top-1 routing and per-expert loops (clear, legible; not optimized for high-performance training). It's suitable for demonstration, debugging, and unit tests.

---

If you want, I can now:
- implement a more efficient routing (batched dispatch) and training helpers (checkpointing, gradient accumulation), or
- add a minimal evaluation/ sampling script and tests.

Which one do you want next? (pick one: `optimizations`, `sampling`, `tests`, or `none`)

---

## Scaling to ~3B parameter training ⚠️

Training the `3b` config requires multi-GPU / multi-node hardware and sharded training (DeepSpeed ZeRO / FSDP). I added a template `deepspeed_config.json` and a sample `run_deepspeed.bat` to help launch distributed jobs. Key points:

- Hardware estimate: at least 8x A100 40GB (or similar) **recommended**; fewer GPUs may work with more aggressive sharding and smaller batch sizes but will be slower.
- Use DeepSpeed (or FSDP) with ZeRO stage 3 and fp16 mixed precision. You will also want to enable expert sharding if using many experts.
- I implemented a `3b` example config in `train.py` (use `--config 3b`), and added top-k gating (configurable `--moe-top-k 1|2`).
- Real training needs: dataset (~10s of GBs for decent convergence), checkpointing, logging, validation loops, and possibly activation checkpointing / gradient checkpointing.

If you want, I can:
- wire up DeepSpeed more fully (tests for small-scale multi-GPU smoke runs), or
- prepare a cloud-ready launch guide (Azure/GC/ AWS instance types, cost estimate), or
- implement more optimized expert dispatch or integrate with a 3rd-party MoE framework.

Tell me which direction you want next and whether you have access to GPUs (how many and what model).