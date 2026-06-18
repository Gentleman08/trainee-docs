# Batch 6 — Fine-Tuning & Training
> How to adapt pre-trained models to your specific task — efficiently and on a budget.

---

## 1. Full Fine-Tuning

### Definition
Updating **all** parameters of a pre-trained model on your own dataset — the most thorough but most expensive adaptation method.

### Real-World Dev Example
You take `bert-base-uncased` and train every one of its 110M parameters on your customer support ticket classification dataset.

```
ASCII: Full Fine-Tuning Flow
Pre-trained Model (frozen weights)
        ↓  Unfreeze ALL layers
  [Layer 1] [Layer 2] ... [Layer N]
        ↓  Train on your data
  Updated Model (all weights changed)
```

### Gotchas & Dev Context
- **Catastrophic forgetting**: the model may lose general knowledge if your dataset is small
- Needs a GPU with enough VRAM to hold the full model + gradients + optimizer states (can be 3–4× model size)
- Learning rate should be **very small** (e.g., `2e-5`) — you're nudging, not retraining from scratch
- Rarely worth it unless you have tens of thousands of task-specific examples
- Always keep a copy of the original weights before fine-tuning

### Production FAQ
**Q: When is full fine-tuning actually worth it?**
A: When you have a large, high-quality domain-specific dataset and need maximum task performance — e.g., fine-tuning a medical LLM on 500k clinical notes.

**Q: How much VRAM does full fine-tuning need?**
A: For a 7B-parameter model in FP32: ~112 GB just for weights. In practice, use mixed precision (FP16/BF16) and optimizer offloading to bring it to ~40–80 GB.

**Q: Can I full fine-tune on a consumer GPU?**
A: Barely. For large models, use LoRA/QLoRA instead. For tiny models (<1B params), a 24 GB GPU is feasible.

---

## 2. LoRA (Low-Rank Adaptation)

### Definition
Instead of updating all weights, LoRA injects small **trainable rank-decomposition matrices** beside frozen layers — giving you 90%+ of fine-tuning quality at a fraction of the compute.

### Real-World Dev Example
You fine-tune `LLaMA-3-8B` for legal document summarization. With LoRA, only ~0.5% of parameters are trained, and you need one GPU instead of four.

```
ASCII: LoRA Mechanism
Original weight matrix W (frozen)
         ↓
  W_new = W + (A × B)
         ↑
  A [d × r]  ×  B [r × k]   ← tiny trainable matrices
  r = rank (e.g. 8, 16, 64)
  d, k = original dimensions
```

### Gotchas & Dev Context
- Key hyperparams: `rank (r)`, `alpha (α)`, `target_modules` (usually `q_proj`, `v_proj`)
- Higher rank = more expressiveness but more VRAM
- `lora_alpha / lora_rank` acts as a learning rate scaling factor — set `alpha = 2 × rank` as a safe default
- Merge LoRA weights back into base model for inference with no latency overhead
- Apply LoRA to attention layers first; adding it to MLP layers can help but adds cost

### Production FAQ
**Q: Does LoRA produce worse results than full fine-tuning?**
A: Often indistinguishable for task-specific fine-tuning. For very large domain shifts, full fine-tuning may edge ahead.

**Q: Can I stack multiple LoRA adapters?**
A: Yes — tools like `peft` support loading and switching adapters, useful for serving multiple task variants from one base model.

**Q: What rank should I use?**
A: Start with `r=16`. Use `r=64` or higher for complex tasks; `r=4` for quick experiments.

---

## 3. QLoRA (Quantized LoRA)

### Definition
LoRA applied to a **4-bit quantized** base model — lets you fine-tune large models (13B, 70B) on a single consumer GPU by drastically reducing memory usage.

### Real-World Dev Example
Fine-tuning `Mistral-7B` on a 24 GB RTX 4090 using QLoRA — something impossible with full fine-tuning or even standard LoRA at FP16.

```
ASCII: QLoRA Memory Savings
Full Fine-Tune 7B (FP32):  ~112 GB
LoRA 7B (FP16):             ~28 GB
QLoRA 7B (4-bit):           ~6–8 GB  ✅ fits on consumer GPU
```

### Gotchas & Dev Context
- Uses `bitsandbytes` NF4 (Normal Float 4) quantization for the base model
- Only the LoRA adapter weights stay in full precision (BF16)
- Training is slower than FP16 LoRA due to dequantization overhead (~20–30% slower)
- Use `double_quantization=True` to save a few more GB with minimal quality loss
- Not ideal for production inference — dequantize or use GGUF/GPTQ for serving

### Production FAQ
**Q: How do I start a QLoRA training run?**
A: Use `transformers` + `peft` + `bitsandbytes`. Load model with `load_in_4bit=True`, then wrap with `get_peft_model()`.

**Q: Is the quality gap between QLoRA and full fine-tuning large?**
A: For most tasks, within 1–2% of full fine-tuning quality. The trade-off is almost always worth it for budget-constrained setups.

**Q: Can I merge QLoRA adapters back?**
A: Yes, but first dequantize the base model to FP16, then merge. You cannot directly merge into a 4-bit model.

---

## 4. PEFT (Parameter-Efficient Fine-Tuning)

### Definition
An umbrella term for methods that adapt a pre-trained model by training **only a small subset of parameters** — LoRA, adapters, prefix tuning, and prompt tuning all fall under PEFT.

### Real-World Dev Example
The Hugging Face `peft` library is the de-facto toolkit: one API to switch between LoRA, IA³, AdaLoRA, or prompt tuning methods.

```python
from peft import get_peft_model, LoraConfig
config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj","v_proj"])
model = get_peft_model(base_model, config)
model.print_trainable_parameters()
# trainable params: 4,194,304 || all params: 6,742,609,920 || trainable%: 0.06%
```

### Gotchas & Dev Context
- PEFT methods differ in *where* they inject trainable parameters — choose based on task and hardware
- Hugging Face `peft` supports: LoRA, QLoRA, IA³, AdaLoRA, Prefix Tuning, Prompt Tuning, LoftQ
- PEFT adapters are tiny (~MB vs GB) — easy to version, store, and switch
- Not all PEFT methods work equally well on all architectures
- `peft` integrates directly with `transformers.Trainer` — minimal boilerplate

### Production FAQ
**Q: Which PEFT method should I pick as a default?**
A: LoRA (or QLoRA if VRAM is tight) — best balance of quality, speed, and simplicity for most LLM tasks.

**Q: Can I combine PEFT with full fine-tuning?**
A: Yes. A common pattern: PEFT first for fast iteration, then optional full fine-tune on the best checkpoint.

---

## 5. Adapter Layers

### Definition
Small bottleneck neural network modules **inserted between transformer layers** — only these adapters are trained, leaving the rest of the model frozen.

### Real-World Dev Example
Original paper (Houlsby et al.) inserts adapter modules after each attention and FFN sub-layer in BERT, training for a new language task in minutes.

```
ASCII: Adapter in a Transformer Layer
  → [Self-Attention] → [Add & Norm]
                            ↓
                     [Adapter Module]   ← trainable
                       (down-proj → activation → up-proj)
                            ↓
  → [Feed-Forward]  → [Add & Norm]
```

### Gotchas & Dev Context
- Adapter modules add **inference latency** (~5–10%) because of the extra forward pass through bottleneck layers — unlike LoRA, they can't be merged away
- Bottleneck dimension (e.g., 64) controls the capacity/speed trade-off
- Less popular now than LoRA due to latency cost, but still used in multi-task and continual learning scenarios
- `AdapterHub` hosts hundreds of pre-trained adapters for common tasks/languages

### Production FAQ
**Q: When would I choose adapters over LoRA?**
A: For multi-task serving — you can hot-swap adapter modules per request without reloading the base model. LoRA requires re-merging or separate inference paths.

**Q: Do adapters work for vision models too?**
A: Yes — adapters have been applied to ViT and multimodal models, not just NLP.

---

## 6. Prefix Tuning / Prompt Tuning

### Definition
Instead of modifying model weights, these methods prepend **learnable virtual tokens** to the input — the model learns which "context" steers it toward the task.

### Real-World Dev Example
For a summarization task, prefix tuning prepends 20 virtual tokens to every input. Only those 20 token embeddings are trained — the rest of GPT-2 stays frozen.

```
ASCII: Prefix Tuning
Input:  [P1][P2]...[Pk] [Real Token 1][Real Token 2]...
         ↑ learnable soft tokens (not real words)
         ↑ only these gradients update
```

### Gotchas & Dev Context
- **Prefix Tuning**: learnable tokens prepended at every layer's key/value — more powerful but complex
- **Prompt Tuning**: learnable tokens only at the input embedding layer — simpler, works well at scale (>1B params)
- Both add **sequence length overhead** — affects speed and context window usage
- Performance approaches full fine-tuning only on very large models (>10B)
- Soft prompts are not human-interpretable — debugging is hard
- Good for quick multi-task switching with a shared base model

### Production FAQ
**Q: Is prompt tuning the same as prompt engineering?**
A: No — prompt engineering uses hand-crafted text; prompt tuning trains continuous (floating-point) token embeddings via gradient descent.

**Q: Which works better on small models?**
A: Neither — both underperform on small models. Use LoRA for <7B models; prompt tuning is best at ≥10B scale.

---

## 7. Dataset Preparation for Fine-Tuning

### Definition
The process of collecting, cleaning, formatting, and tokenizing your data into a structure the model can learn from — arguably the most impactful step in fine-tuning.

### Real-World Dev Example
You scrape 10k customer support Q&A pairs, deduplicate them, remove PII, format them as instruction-response pairs, and tokenize with a max length of 2048 tokens.

### Gotchas & Dev Context
- **Quality > Quantity**: 1,000 clean, diverse examples often beat 100,000 noisy ones
- Always **shuffle** your dataset — sequential patterns introduce biases
- Split into train/val/test (e.g., 90/5/5) — never evaluate on training data
- **Tokenization gotcha**: truncating too aggressively loses answer context; too lenient → OOM
- Check for **data leakage** — test prompts must not appear in training set
- Deduplicate with tools like `datasketch` MinHash — near-duplicate data inflates metrics without improving generalization
- Set `ignore_index=-100` on input tokens when computing loss — only train on the response portion

```python
# Mask input tokens from loss
labels = input_ids.clone()
labels[:prompt_len] = -100  # don't train on the prompt
```

### Production FAQ
**Q: How many examples do I need?**
A: For task-specific fine-tuning: 500–5,000 high-quality pairs is often enough. For broad domain adaptation: 50k+.

**Q: Should I upsample rare classes?**
A: Yes — class imbalance causes the model to ignore minority outputs. Upsample or use weighted loss.

---

## 8. Instruction Dataset Format (Alpaca, ShareGPT)

### Definition
Standardized schemas for formatting fine-tuning data as instructions and responses — the format you pick determines how the model learns to follow instructions.

### Real-World Dev Example
You build a coding assistant and format 3,000 examples in ShareGPT style to train a conversational model that maintains multi-turn context.

```
ASCII: Two Common Formats

── Alpaca Format ──────────────────────
{
  "instruction": "Summarize the text.",
  "input": "The Eiffel Tower is...",
  "output": "The Eiffel Tower is a landmark in Paris."
}

── ShareGPT Format ────────────────────
{
  "conversations": [
    {"from": "human", "value": "Explain recursion."},
    {"from": "gpt",   "value": "Recursion is when a function calls itself..."},
    {"from": "human", "value": "Give me an example."},
    {"from": "gpt",   "value": "def factorial(n): ..."}
  ]
}
```

### Gotchas & Dev Context
- **Alpaca**: good for single-turn instruction following; simple but loses conversation history
- **ShareGPT**: multi-turn conversations; better for chat models; more complex to process
- Apply the model's **chat template** during tokenization — e.g., `tokenizer.apply_chat_template()` — wrong templates silently hurt quality
- Mixing both formats in one training run is possible with tools like Axolotl

### Production FAQ
**Q: Which format should I use for a chatbot?**
A: ShareGPT — it preserves multi-turn context. Alpaca is fine for single-turn task models.

**Q: Does the dataset format affect inference?**
A: Yes — you must use the **same chat template** at inference as during training, or the model will produce garbage.

---

## 9. Training Frameworks (Hugging Face Trainer, Axolotl, LLaMA Factory)

### Definition
Software libraries that handle the training loop, logging, checkpointing, and distributed setup so you focus on data and config rather than boilerplate.

### Real-World Dev Example
You use **Axolotl** with a single YAML config to QLoRA-fine-tune `Mistral-7B` on a ShareGPT dataset across 2 GPUs — no custom training loop needed.

| Framework | Best For | Key Feature |
|---|---|---|
| HF Trainer | Flexibility, research | Deep ecosystem integration |
| Axolotl | Fast LLM fine-tuning | YAML config, multi-format datasets |
| LLaMA Factory | Beginner-friendly | Web UI + CLI, broad model support |

### Gotchas & Dev Context
- **HF Trainer**: most flexible but needs more code; use `TrainingArguments` to configure everything
- **Axolotl**: opinionated but powerful; great for production fine-tuning pipelines; active community
- **LLaMA Factory**: best for non-engineers or fast prototyping; supports LoRA, QLoRA, full FT
- All three support DeepSpeed and FSDP for distributed training
- Axolotl and LLaMA Factory both support gradient checkpointing, packing, and flash attention out-of-the-box

### Production FAQ
**Q: Which framework is best for production?**
A: Axolotl for engineering teams — reproducible configs, CI-friendly, good logging. LLaMA Factory if the team prefers UI workflows.

**Q: Can I switch frameworks mid-project?**
A: Usually yes — all output standard HF-compatible checkpoints. Migration is a config rewrite, not a code rewrite.

---

## 10. Distributed Training (DDP, FSDP, DeepSpeed)

### Definition
Techniques for training models across **multiple GPUs or machines** by splitting data, model, or both — necessary when a model or batch doesn't fit on a single GPU.

### Real-World Dev Example
You train a 70B model on 8×A100s using DeepSpeed ZeRO-3, which shards optimizer states, gradients, and parameters across all GPUs.

```
ASCII: DDP vs FSDP vs DeepSpeed
DDP (Data Parallel):
  GPU0: [Full Model] ← batch shard A
  GPU1: [Full Model] ← batch shard B
  → sync gradients after each step

FSDP (Fully Sharded):
  GPU0: [Model Shard 1] ← batch shard A
  GPU1: [Model Shard 2] ← batch shard B
  → gather weights only when needed

DeepSpeed ZeRO-3:
  Shards params + gradients + optimizer states
  Offload to CPU/NVMe if needed
```

### Gotchas & Dev Context
- **DDP**: easiest to set up; each GPU holds a full model copy — limits max model size
- **FSDP**: native PyTorch; shards model across GPUs; steeper learning curve; good for 10B+ models
- **DeepSpeed ZeRO**: most aggressive memory savings; ZeRO-3 + CPU offload can train 70B on 8×80GB GPUs
- Communication overhead increases with more GPUs — don't assume linear scaling
- Use `accelerate launch` or `torchrun` as launchers; DeepSpeed uses `deepspeed` CLI

### Production FAQ
**Q: Which should I start with?**
A: DDP if your model fits on a single GPU (just scaled to more). FSDP or DeepSpeed if it doesn't.

**Q: Does DeepSpeed work with Hugging Face Trainer?**
A: Yes — pass a `deepspeed_config.json` to `TrainingArguments(deepspeed=...)`. Minimal code change.

---

## 11. Mixed Precision Training (FP16, BF16)

### Definition
Training with lower-precision floating-point numbers (16-bit instead of 32-bit) to cut memory usage and speed up training — with minimal impact on accuracy when done right.

### Real-World Dev Example
Switching from FP32 to BF16 halves the VRAM usage from 28 GB to 14 GB when training a 7B model, allowing a larger batch size on the same hardware.

```
ASCII: Float Formats
FP32:  1 sign | 8 exponent | 23 mantissa  (stable, large range)
FP16:  1 sign | 5 exponent | 10 mantissa  (fast, but can overflow)
BF16:  1 sign | 8 exponent | 7 mantissa   (same range as FP32, fewer decimals)
```

### Gotchas & Dev Context
- **FP16**: fast on older GPUs (V100); risk of numeric overflow/underflow — use **loss scaling** to compensate
- **BF16**: preferred on Ampere+ GPUs (A100, 3090, 4090) — same dynamic range as FP32, much safer
- Always keep a FP32 "master copy" of weights for the optimizer — only forward/backward pass uses FP16/BF16
- Set `bf16=True` in `TrainingArguments` if your GPU supports it; fall back to `fp16=True` otherwise
- Use `torch.cuda.is_bf16_supported()` to check at runtime

### Production FAQ
**Q: Can mixed precision training hurt model quality?**
A: Rarely for BF16. FP16 can cause loss spikes if loss scaling is misconfigured. Monitor loss curves.

**Q: Which should I choose, FP16 or BF16?**
A: BF16 on Ampere/Hopper GPUs. FP16 for older hardware. BF16 is always preferred when available.

---

## 12. Gradient Accumulation

### Definition
Simulating a large batch size by accumulating gradients over several small batches before updating weights — works around VRAM limits without sacrificing effective batch size.

### Real-World Dev Example
You can only fit batch size 4 on your GPU, but research shows batch size 32 trains better. Set `gradient_accumulation_steps=8` — weights update every 8 mini-batches.

```
ASCII: Gradient Accumulation (steps=4)
Step 1: forward+backward (batch A) → accumulate grads
Step 2: forward+backward (batch B) → accumulate grads
Step 3: forward+backward (batch C) → accumulate grads
Step 4: forward+backward (batch D) → UPDATE weights, zero grads
         ↑ effective batch = 4 × batch_size
```

### Gotchas & Dev Context
- Effective batch size = `batch_size_per_gpu × gradient_accumulation_steps × num_gpus`
- Does **not** reduce VRAM for the forward pass — only helps fit larger logical batches
- Logging and evaluation should happen per **effective step**, not per mini-batch
- Batch norm layers behave differently under accumulation — less of a concern for transformers
- Tune learning rate alongside batch size (linear scaling rule: `lr ∝ batch_size`)

### Production FAQ
**Q: Does gradient accumulation slow training?**
A: Slightly — extra forward/backward passes without optimizer steps. But it's far cheaper than getting a bigger GPU.

**Q: How do I set it in Hugging Face Trainer?**
A: `TrainingArguments(gradient_accumulation_steps=8)` — that's it.

---

## 13. Gradient Checkpointing

### Definition
A memory-saving technique that **discards intermediate activations** during the forward pass and recomputes them during backprop — trades compute for memory.

### Real-World Dev Example
Training a 7B model without gradient checkpointing needs ~40 GB for activations alone. Enabling it cuts this to ~8 GB, at the cost of ~20–30% slower training.

```
ASCII: Normal vs Checkpointing
Normal:
  Forward: save ALL activations → [A1][A2][A3]...[AN] in memory
  Backward: use saved activations for gradients

Checkpointing:
  Forward: save only CHECKPOINT activations → [A1]...[AN/k]
  Backward: recompute missing activations on-the-fly
```

### Gotchas & Dev Context
- Enable with `model.gradient_checkpointing_enable()` or `TrainingArguments(gradient_checkpointing=True)`
- The memory vs. speed trade-off is roughly: **saves 60–70% activation memory, costs ~20–30% speed**
- Combine with QLoRA for maximum VRAM savings on consumer hardware
- Some models require `use_reentrant=False` to avoid autograd errors — check model docs
- Incompatible with some custom CUDA kernels — test carefully

### Production FAQ
**Q: Should I always use gradient checkpointing?**
A: Enable it when VRAM is a constraint. If you have headroom, skip it for faster training.

**Q: Does it affect model quality?**
A: No — mathematically identical to normal training. Only speed/memory differs.

---

## 14. Model Parallelism vs Data Parallelism

### Definition
Two strategies for multi-GPU training: **data parallelism** splits the dataset across GPUs (each has a full model copy), while **model parallelism** splits the model itself across GPUs.

### Real-World Dev Example
Finetuning a 7B model: use data parallelism across 4 GPUs. Training a 175B model that doesn't fit in a single GPU: use model parallelism.

```
ASCII: Data vs Model Parallelism
Data Parallelism:
  GPU0: [Full Model] → batch A
  GPU1: [Full Model] → batch B
  → gradients averaged across GPUs

Model Parallelism:
  GPU0: [Layers 1–16] → forward
  GPU1: [Layers 17–32] → forward (receives GPU0's output)
  → one batch, split model
```

### Gotchas & Dev Context
- **Data parallelism** (DDP) is simpler but requires each GPU to hold the full model
- **Model parallelism** introduces pipeline bubbles — GPUs wait for the prior stage to finish
- In practice, most large-scale training uses **both** (hybrid parallelism)
- Tensor parallelism (Megatron-style) is a form of model parallelism — splits individual layer computations
- FSDP and DeepSpeed ZeRO blur the line by sharding model state across data-parallel ranks

### Production FAQ
**Q: When does model parallelism become necessary?**
A: When the model doesn't fit in a single GPU's VRAM even with quantization and gradient checkpointing.

**Q: Does model parallelism work with Hugging Face Trainer?**
A: Basic pipeline parallelism can be configured via `device_map`. For advanced setups, use DeepSpeed or Megatron-LM.

---

## 15. Tensor Parallelism / Pipeline Parallelism

### Definition
**Tensor parallelism** splits individual weight matrices across GPUs; **pipeline parallelism** assigns different model layers to different GPUs and processes batches as a pipeline.

### Real-World Dev Example
Training GPT-3 at OpenAI used 8-way tensor parallelism (split each attention head across 8 GPUs) combined with 64-way pipeline parallelism across nodes.

```
ASCII: Pipeline Parallelism (4 stages)
  Stage 0 (GPU0): Embed + Layers 1–8
  Stage 1 (GPU1): Layers 9–16
  Stage 2 (GPU2): Layers 17–24
  Stage 3 (GPU3): Layers 25–32 + Head

  Micro-batch pipeline:
  GPU0: [B1]→ [B2]→ [B3]→ idle
  GPU1: idle→ [B1]→ [B2]→ [B3]
  GPU2: ...         [B1]→ [B2]→
```

### Gotchas & Dev Context
- **Pipeline bubbles**: GPUs sit idle at the start and end of each batch — mitigate with micro-batching
- Tensor parallelism requires **fast NVLink** between GPUs — bad across nodes
- Pipeline parallelism tolerates higher latency (PCIe, InfiniBand) — better across nodes
- Implemented in: **Megatron-LM**, **DeepSpeed**, **NVIDIA NeMo**
- Combination of tensor + pipeline + data parallelism = **3D parallelism** (used at 100B+ scale)

### Production FAQ
**Q: Do I need these for fine-tuning?**
A: Rarely — these shine at pre-training scale. For fine-tuning, FSDP or DeepSpeed ZeRO is usually enough.

**Q: What's the easiest way to enable pipeline parallelism?**
A: Use DeepSpeed with `pipeline_parallel_size` set in the config, or use `device_map="auto"` in HF for naive layer distribution.

---

## 16. Training Loss Curves / Evaluation Metrics

### Definition
Visual plots of how training and validation loss change over time — your primary signal for diagnosing whether training is going well, overfitting, or diverging.

### Real-World Dev Example
You fine-tune a model for 3 epochs and plot loss per step. Train loss drops smoothly; validation loss flattens at epoch 2, then rises — classic overfitting signal.

```
ASCII: Loss Curve Patterns
Loss
 │ \
 │  \___         ← Good: both losses converge
 │       \___
 └─────────────► Steps

Loss
 │ \
 │  \____        ← Overfit: val loss rises after dip
 │       \  /‾‾
 └─────────────► Steps (train=solid, val=dashed)

Loss
 │
 │ ~~~~~~~~~~~   ← Bad LR: loss oscillates, not converging
 └─────────────► Steps
```

### Gotchas & Dev Context
- Log both train and **validation** loss — train loss alone is meaningless
- Use **Weights & Biases (wandb)**, TensorBoard, or MLflow for real-time monitoring
- Loss should be **monotonically decreasing on average** — spikes are a red flag
- Eval too infrequently → miss overfitting; too frequently → slows training
- NaN loss = likely LR too high, bad data (null labels), or FP16 overflow

### Production FAQ
**Q: My train loss is low but val loss is high — what do I do?**
A: Overfitting. Reduce epochs, add more data, use stronger regularization, or lower rank (for LoRA).

**Q: How often should I evaluate?**
A: Every 10–20% of an epoch is a common rule. For long runs, evaluate every N steps.

---

## 17. BLEU / ROUGE / METEOR (NLP Metrics)

### Definition
Automated reference-based metrics that compare a model's generated text to human-written references — useful for fast evaluation of translation, summarization, and generation quality.

### Real-World Dev Example
Your summarization model generates 1,000 test summaries. You compute ROUGE-L against human summaries to compare checkpoints before expensive human evaluation.

| Metric | Best For | How It Works |
|---|---|---|
| BLEU | Translation | n-gram precision (how many model n-grams match reference) |
| ROUGE | Summarization | n-gram recall (how many reference n-grams appear in output) |
| METEOR | Translation | Precision + recall + synonyms + stemming |

### Gotchas & Dev Context
- **BLEU** penalizes short outputs (brevity penalty) — high BLEU ≠ good text
- **ROUGE-1/2**: unigram/bigram overlap; **ROUGE-L**: longest common subsequence
- All three have **low correlation with human judgment** for open-ended generation tasks
- Don't use these as the sole production metric — complement with LLM-as-judge or human eval
- Use `sacrebleu` for standardized, reproducible BLEU scores; `rouge_score` for ROUGE

```python
from rouge_score import rouge_scorer
scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
scores = scorer.score("model output here", "reference text here")
```

### Production FAQ
**Q: Which metric should I use for summarization?**
A: ROUGE-L as a baseline, but always run human evaluation or GPT-4-as-judge before deploying.

**Q: My BLEU score is 0.3 — is that good?**
A: Depends heavily on the task. For MT: 0.3–0.4 is competitive. For abstractive summarization, BLEU scores are often below 0.2 and not reliable.

---

## 18. Perplexity

### Definition
A measure of how **surprised** a language model is by a text — lower perplexity means the model assigns high probability to the correct next tokens, indicating better language modeling.

### Real-World Dev Example
You fine-tune a model on medical text. Before fine-tuning, perplexity on medical reports is 85. After fine-tuning, it drops to 12 — the model has learned the domain vocabulary and structure.

```
ASCII: Perplexity Intuition
Perplexity = 2^(cross-entropy loss)

Loss = 1.0 → Perplexity ≈ 2.7   (model is confident)
Loss = 3.0 → Perplexity ≈ 20    (model is uncertain)
Loss = 6.0 → Perplexity ≈ 403   (model is very confused)

A perplexity of N ≈ model is as confused as
choosing uniformly from N words
```

### Gotchas & Dev Context
- Only comparable between models using the **same tokenizer and vocabulary**
- Lower is better, but not always better for downstream tasks — a model can have low perplexity and still be bad at instruction following
- Used heavily for **base model evaluation** and comparing pre-training runs
- Perplexity on the test set is a standard LM benchmark — but don't over-optimize for it
- Compute with `model.eval()` + no gradient, using `torch.nn.CrossEntropyLoss`

```python
import torch
loss = model(input_ids, labels=input_ids).loss
perplexity = torch.exp(loss).item()
```

### Production FAQ
**Q: Can I use perplexity to compare two different model families?**
A: No — different tokenizers produce incomparable perplexity scores. Use task-specific benchmarks instead.

**Q: Does perplexity tell me how good my fine-tuned model is?**
A: Partially. It measures language modeling quality, not instruction-following or factual accuracy. Use it alongside task-specific metrics.

---

*End of Batch 6 — Fine-Tuning & Training*
