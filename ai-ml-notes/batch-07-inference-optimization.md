# Batch 7 — Inference & Optimization
> Making models fast, cheap, and production-ready without sacrificing accuracy.

---

## 1. Model Quantization (INT8, INT4, GPTQ, AWQ, GGUF)

### Definition
Quantization reduces a model's numerical precision (e.g., from 32-bit floats to 8-bit or 4-bit integers) to shrink its memory footprint and speed up inference — with minimal accuracy loss.

### Real-World Dev Example
A 70B LLaMA model needs ~140 GB in FP16. With 4-bit GPTQ quantization, it drops to ~35 GB — fitting on a single 40 GB A100.

```
FP32 weight: 3.14159265  →  4 bits: ~3.1  (good enough!)
```

### ASCII Diagram
```
FP32 (32 bits) → INT8 (8 bits) → INT4 (4 bits)
[████████████████]  →  [████████]  →  [████]
   More accurate          Balanced        Tiny & fast
```

### Gotchas & Dev Context
- **INT8** — safe for most tasks; minimal accuracy drop
- **INT4** — aggressive; use GPTQ or AWQ for calibrated quantization
- **GPTQ** — post-training quantization, layer-by-layer; popular for LLMs
- **AWQ** — activation-aware; better quality than GPTQ at same bit width
- **GGUF** — file format used by `llama.cpp` for CPU/GPU hybrid inference
- Quantizing embeddings separately from attention layers preserves quality
- Always benchmark on your task — perplexity alone doesn't tell the full story

### Production FAQ
**Q: Can I quantize any model?**
A: Yes, but decoder-only LLMs (GPT-style) respond better than encoder models like BERT. Vision models may need extra care.

**Q: GPTQ vs AWQ — which should I pick?**
A: AWQ generally preserves accuracy better, especially at INT4. Use GPTQ if you need broader toolchain support.

**Q: Does quantization affect output quality noticeably?**
A: At INT8, rarely. At INT4, you may see degradation on complex reasoning. Run evals on your specific use case.

---

## 2. Pruning

### Definition
Pruning removes redundant weights or neurons from a trained model, reducing its size and compute cost — similar to trimming dead branches from a tree.

### Real-World Dev Example
A BERT model fine-tuned for sentiment analysis has many near-zero attention heads. Removing 30% of them cuts inference time by 25% with <1% accuracy drop.

### ASCII Diagram
```
Before Pruning:        After Pruning:
[W1][W2][W3][W4]  →  [W1][  ][W3][  ]
[W5][W6][W7][W8]  →  [  ][W6][  ][W8]
   Dense network         Sparse network (faster)
```

### Gotchas & Dev Context
- **Unstructured pruning** — zeroes out individual weights; requires sparse-aware hardware to see speedups
- **Structured pruning** — removes entire heads/layers/channels; immediately faster on any hardware
- Pruning after fine-tuning ("prune then retrain") beats pruning from scratch
- Use iterative pruning: prune 10% → retrain → prune 10% → retrain
- Most popular library: `torch.nn.utils.prune` or Hugging Face `optimum`
- Don't prune the final classification head — it's small and critical

### Production FAQ
**Q: How much can I prune without hurting accuracy?**
A: Typically 20–40% of weights safely. Beyond 50%, expect meaningful accuracy loss unless you retrain aggressively.

**Q: Is pruning better than quantization?**
A: They complement each other. Quantization is usually more immediately impactful. Combine both for maximum compression.

**Q: Does pruning work on LLMs?**
A: Yes — SparseGPT and Wanda are popular methods for LLM pruning without retraining.

---

## 3. Knowledge Distillation

### Definition
A smaller "student" model is trained to mimic the outputs of a larger "teacher" model — inheriting its knowledge at a fraction of the size.

### Real-World Dev Example
DistilBERT is a distilled BERT: 40% smaller, 60% faster, but retains 97% of BERT's accuracy on GLUE benchmarks.

### ASCII Diagram
```
Teacher Model (Large)         Student Model (Small)
  [GPT-4 / BERT-large]   →→→  [DistilBERT / TinyGPT]
   Soft logits/outputs          Learns to match them
        ↓                              ↓
   High accuracy              Fast + nearly as accurate
```

### Gotchas & Dev Context
- Student trains on **soft labels** (probability distributions), not hard 0/1 labels — this carries richer signal
- Temperature scaling (T > 1) softens teacher outputs to reveal inter-class relationships
- Works best when student and teacher share similar architectures (same family)
- Task-specific distillation > general distillation for production deployment
- Requires access to teacher outputs (or logits) — black-box APIs make this harder
- Libraries: Hugging Face `optimum`, `txtai`, custom PyTorch training loops

### Production FAQ
**Q: Can I distill a proprietary model like GPT-4?**
A: Only via output matching on labeled data (no logit access). This is "black-box" distillation — less efficient but feasible.

**Q: When should I use distillation over quantization?**
A: Distillation when you want a permanently smaller, retrainable model. Quantization when you want a quick size reduction of an existing checkpoint.

**Q: How long does distillation take?**
A: Expect 20–50% of the teacher's original training time. Still cheaper than training from scratch.

---

## 4. ONNX (Open Neural Network Exchange)

### Definition
ONNX is an open format that lets you export a model from one framework (PyTorch, TensorFlow) and run it in another runtime or on different hardware — a universal adapter for ML models.

### Real-World Dev Example
You train a model in PyTorch, export it to ONNX, then deploy it with ONNX Runtime on a Windows edge device — no PyTorch installation required.

```python
import torch.onnx
torch.onnx.export(model, dummy_input, "model.onnx")
```

### ASCII Diagram
```
[PyTorch]  ──┐
[TensorFlow] ─┤──→ [.onnx file] ──→ [ONNX Runtime]
[JAX]      ──┘                        [TensorRT]
                                       [OpenVINO]
                                       [CoreML]
```

### Gotchas & Dev Context
- Always verify exported model with `onnxruntime` before shipping — dynamic shapes can cause issues
- Use `opset_version=17` or latest; older opsets miss newer ops
- Dynamic axes must be declared explicitly for variable batch sizes
- Not all custom ops export cleanly — check operator support list
- `onnxsim` (simplifier) reduces graph complexity post-export
- ONNX Runtime is often faster than native PyTorch for CPU inference

### Production FAQ
**Q: Is ONNX lossless?**
A: Yes for standard ops — numerically identical outputs. Custom ops or exotic layers may need manual mapping.

**Q: Can I fine-tune an ONNX model?**
A: No. ONNX is inference-only. Fine-tune in your source framework, then re-export.

**Q: ONNX vs TorchScript — which to use?**
A: ONNX for cross-framework/cross-device portability. TorchScript for staying within the PyTorch ecosystem.

---

## 5. TensorRT

### Definition
NVIDIA's inference optimization engine that compiles and fuses neural network layers specifically for NVIDIA GPUs — achieving 2–10× speedups over raw PyTorch.

### Real-World Dev Example
A ResNet-50 image classifier runs at 200 FPS in PyTorch. After TensorRT optimization with FP16, it hits 900 FPS on the same A10G GPU.

### ASCII Diagram
```
PyTorch Model
     ↓
[TensorRT Engine Builder]
     ↓  (layer fusion, precision calibration, kernel tuning)
[Compiled .trt Engine]
     ↓
GPU Inference (2–10× faster)
```

### Gotchas & Dev Context
- Compiled engines are **GPU-specific** — you can't move a `.trt` file between GPU families
- Rebuild engine when upgrading TensorRT versions or switching GPU types
- INT8 calibration requires a calibration dataset (~500 representative samples)
- Dynamic shapes add overhead — use fixed batch sizes where possible
- Use `torch2trt` or Hugging Face `optimum` for easier PyTorch → TRT pipelines
- Not all ops are TRT-supported; unsupported ops fall back to PyTorch (slow path)

### Production FAQ
**Q: How much speedup should I realistically expect?**
A: 2–4× for most transformer models, up to 10× for CNNs with many fusable layers.

**Q: Do I need to recompile for every deployment?**
A: Yes, per GPU SKU and TRT version. Automate engine building as part of your CI/CD pipeline.

**Q: TensorRT vs ONNX Runtime with CUDA — which is faster?**
A: TensorRT wins on NVIDIA GPUs for heavy workloads. ONNX Runtime with CUDA provider is simpler to set up and often good enough.

---

## 6. vLLM / TGI (Text Generation Inference)

### Definition
Optimized serving frameworks built specifically for large language models — handling batching, memory management, and throughput at production scale far beyond naïve HuggingFace `model.generate()`.

### Real-World Dev Example
Serving LLaMA-3 70B with `model.generate()` handles ~2 req/sec. Switching to vLLM with PagedAttention brings this to ~20 req/sec on the same hardware.

### ASCII Diagram
```
Without vLLM/TGI:         With vLLM/TGI:
Req1 → GPU → wait         Req1 ─┐
Req2 → GPU → wait         Req2 ─┤→ [Continuous Batch] → GPU
Req3 → GPU → wait         Req3 ─┘         (all together)
(sequential, slow)                         (10× throughput)
```

### Gotchas & Dev Context
- **vLLM** — PagedAttention manages KV cache like virtual memory; best for high-concurrency
- **TGI** (HuggingFace) — production-ready, Docker-first, supports flash attention & quantization
- vLLM has a simpler OpenAI-compatible API out of the box
- Both support streaming, tensor parallelism, and quantized models
- Cold start still applies — first request after load is slow
- Monitor KV cache utilization; cache exhaustion degrades throughput sharply

### Production FAQ
**Q: vLLM or TGI — which should I start with?**
A: vLLM for OpenAI-compatible drop-in API and simpler setup. TGI for deep HuggingFace integration and enterprise support.

**Q: Can these serve multiple models simultaneously?**
A: Not natively in a single instance. Use separate instances per model or a routing layer (e.g., Traefik, Ray Serve).

**Q: What's the minimum GPU requirement?**
A: vLLM needs CUDA and at least 8 GB VRAM for small models (7B at 4-bit). TGI similarly.

---

## 7. Batched Inference

### Definition
Processing multiple inputs together in a single forward pass instead of one at a time — dramatically improving GPU utilization and throughput.

### Real-World Dev Example
An image classification service receives 100 photos/sec. Processing one-by-one wastes 80% of GPU capacity. Batching groups of 32 images multiplies throughput 8×.

### ASCII Diagram
```
No Batching:            Batched (batch=4):
[img1] → GPU → result   [img1]
[img2] → GPU → result   [img2]  → GPU → [r1, r2, r3, r4]
[img3] → GPU → result   [img3]
[img4] → GPU → result   [img4]
  4 round trips             1 round trip (4× faster)
```

### Gotchas & Dev Context
- Larger batches = higher throughput but higher latency per request
- Batch size is limited by VRAM — `OOM` errors mean reduce batch size
- Padding is required when input lengths vary (masks tell model to ignore padding)
- For LLMs, naïve static batching is inefficient; prefer continuous batching (see §9)
- Optimal batch size is hardware-dependent — benchmark with powers of 2 (8, 16, 32, 64)
- Dynamic batching (collect requests within a time window) balances latency and throughput

### Production FAQ
**Q: What batch size should I start with?**
A: Start at 32 and halve until no OOM. Then benchmark latency at each level to find your sweet spot.

**Q: Does batching affect model accuracy?**
A: No — the math is identical. Results are the same as running individually.

**Q: How do I implement dynamic batching?**
A: Use Triton Inference Server's dynamic batcher, or vLLM/TGI which handle it automatically for LLMs.

---

## 8. Speculative Decoding

### Definition
A fast "draft" model generates several candidate tokens, then the large "target" model verifies them all in parallel — recovering the target model's quality at the draft model's speed.

### Real-World Dev Example
Using LLaMA-7B as the draft and LLaMA-70B as the verifier: the 70B model only does one forward pass per 4–5 tokens instead of one per token. 2–3× speedup with identical outputs.

### ASCII Diagram
```
Normal Decoding:
70B: [tok1] → [tok2] → [tok3] → [tok4]   (4 serial passes)

Speculative Decoding:
7B (draft):  [tok1, tok2, tok3, tok4]    (1 fast pass)
70B (verify): [✓tok1, ✓tok2, ✗tok3]     (1 parallel pass)
→ Accept tok1, tok2; resample from tok3
```

### Gotchas & Dev Context
- Draft and target must share the **same tokenizer**
- Speedup depends on draft acceptance rate — mismatched domains hurt badly
- No accuracy loss: rejected draft tokens are resampled from the target distribution
- Works best for tasks with predictable outputs (code, structured data)
- Integrated into vLLM and TGI — minimal setup needed
- Draft model adds VRAM overhead — plan accordingly

### Production FAQ
**Q: Is the output exactly the same as running the big model alone?**
A: Yes — mathematically equivalent. Rejected tokens are resampled correctly.

**Q: What draft model should I use?**
A: Same model family, 7–10× smaller. LLaMA-7B drafts for LLaMA-70B, Gemma-2B for Gemma-27B.

**Q: When does speculative decoding NOT help?**
A: Low acceptance rate scenarios: diverse creative tasks, domain mismatch, or very short sequences.

---

## 9. Continuous Batching

### Definition
Instead of waiting for an entire batch to finish before accepting new requests, new requests are slotted in the moment a sequence finishes — keeping the GPU 100% busy.

### Real-World Dev Example
Static batching: 8 requests start together; 7 finish fast but GPU waits idle for the 1 long sequence. Continuous batching: as each finishes, a new request immediately takes its slot.

### ASCII Diagram
```
Static Batching:
Slot1: [req1 ████████████]
Slot2: [req2 ███] [IDLE  ]   ← GPU wasted
Slot3: [req3 █████] [IDLE ]

Continuous Batching:
Slot1: [req1 ████████████]
Slot2: [req2 ███][req4 ██]   ← No idle time
Slot3: [req3 █████][req5 ]
```

### Gotchas & Dev Context
- Default in vLLM and TGI — you get it for free
- Critical for LLM APIs with mixed-length outputs (chat vs. summarization)
- Requires a runtime that can handle variable-length in-flight sequences
- Pairs with PagedAttention (vLLM) to manage KV cache slots dynamically
- Increases complexity of priority scheduling (long requests can starve)
- Monitor queue depth and preemption rates in production dashboards

### Production FAQ
**Q: Does continuous batching affect output quality?**
A: No. Each sequence is still generated independently and correctly.

**Q: Should I implement this myself?**
A: No — use vLLM or TGI. Building it correctly is non-trivial.

**Q: How is this different from dynamic batching?**
A: Dynamic batching groups requests before they start. Continuous batching manages requests mid-generation.

---

## 10. Model Serving (Triton, BentoML, Ray Serve)

### Definition
Model serving frameworks wrap your trained model in a production-ready API server with features like batching, versioning, scaling, and monitoring.

### Real-World Dev Example
You deploy a fine-tuned BERT classifier via BentoML: one command packages model + dependencies into a Docker image with a REST API, health checks, and auto-scaling hooks.

### ASCII Diagram
```
Client Request
     ↓
[Load Balancer]
     ↓
[Serving Framework]  ← (Triton / BentoML / Ray Serve)
  ├── Batching
  ├── Model Versioning
  ├── GPU Scheduling
  └── Metrics / Logging
     ↓
[Model(s)] → Response
```

### Gotchas & Dev Context
- **Triton** (NVIDIA) — multi-framework, high-performance, ideal for GPU clusters; steeper learning curve
- **BentoML** — Python-native, easiest DX, great for rapid deployment; less bare-metal control
- **Ray Serve** — best for complex pipelines (multi-model, A/B testing, preprocessing chains)
- All three support model versioning and rolling updates
- Triton supports ensemble pipelines (chain preprocessing → model → postprocessing)
- Pick based on team expertise: BentoML for startups, Triton/Ray for large-scale infra

### Production FAQ
**Q: Which framework scales best for high traffic?**
A: Triton for pure inference throughput on GPU clusters. Ray Serve for multi-step pipelines with scale-out needs.

**Q: Can I switch frameworks later?**
A: Yes, but it requires repackaging. Standardize on one early; abstractions like BentoML reduce lock-in.

**Q: Do these handle authentication and rate limiting?**
A: Not natively — place an API gateway (Kong, AWS API Gateway) in front.

---

## 11. Latency vs Throughput

### Definition
**Latency** = time to complete one request. **Throughput** = total requests completed per second. They trade off against each other and must be optimized for your use case.

### Real-World Dev Example
A chatbot needs low latency (<500ms per token). A bulk document classifier cares about throughput (1000 docs/min). Same model, different optimization strategy.

### ASCII Diagram
```
Low Latency Mode:           High Throughput Mode:
  batch_size = 1              batch_size = 64
  priority: speed             priority: efficiency
  1 req → result fast         64 reqs → results together
  [█]→result                  [████████████████████████]→results
  50ms/req, 20 req/sec        300ms/req, 200 req/sec
```

### Gotchas & Dev Context
- Increasing batch size always improves throughput but increases latency
- Latency has two parts: **TTFT** (Time to First Token) and **TBT** (Time Between Tokens) for streaming
- Use **p99 latency**, not average — averages hide tail latency spikes
- Latency is bounded by serial operations; throughput by parallelism
- Profile with realistic traffic patterns, not synthetic benchmarks
- Caching (§16) is the single biggest latency win for repeated queries

### Production FAQ
**Q: Which should I optimize first?**
A: Depends on your SLA. User-facing apps → latency. Async batch jobs → throughput.

**Q: What's a good latency target for LLM APIs?**
A: TTFT < 500ms, TBT < 50ms for a good user experience. Adjust based on your product.

**Q: How do I measure these reliably?**
A: Use `locust` or `k6` for load testing. Log p50/p95/p99 latency, not just averages.

---

## 12. Tokens Per Second (TPS)

### Definition
TPS measures how many output tokens a model generates per second — the primary performance metric for LLM inference systems.

### Real-World Dev Example
GPT-4 via API delivers ~50 TPS. Your self-hosted LLaMA-3 70B on an A100 delivers ~30 TPS. At 20 TPS, text streams visibly smoothly; below 10 TPS, users notice lag.

### ASCII Diagram
```
Time:     0s      1s      2s
Tokens:   |████████|████████|████████|
           ~30 tok  ~30 tok  ~30 tok
           = 30 TPS (tokens per second)
```

### Gotchas & Dev Context
- TPS varies with **sequence length** — longer KV cache = slower generation
- Batch TPS (aggregate) ≠ per-request TPS — distinguish in benchmarks
- Quantization (INT4) typically 1.5–3× TPS improvement over FP16
- Flash Attention 2 gives 20–30% TPS boost for free via `attn_implementation="flash_attention_2"`
- TPS benchmarks must specify hardware, model size, batch size, and sequence length to be meaningful
- Prefill (prompt processing) and decode (generation) have different TPS — both matter

### Production FAQ
**Q: What TPS is "good" for production?**
A: For chat: >20 TPS per user for smooth streaming. For batch: maximize aggregate TPS within budget.

**Q: How do I increase TPS without new hardware?**
A: Quantize the model, enable Flash Attention, use continuous batching, and increase batch size.

**Q: Does TPS degrade under load?**
A: Yes — as concurrent requests increase, per-user TPS drops. Benchmark at your expected concurrency level.

---

## 13. GPU Memory (VRAM) Estimation

### Definition
Estimating how much GPU RAM a model needs for inference — critical to avoid OOM errors and choose the right hardware.

### Real-World Dev Example
Before renting a cloud GPU to serve LLaMA-3 8B, you estimate: 8B × 2 bytes (FP16) = 16 GB just for weights. Add KV cache + activations → need a 24 GB GPU minimum.

### ASCII Diagram
```
Total VRAM ≈ Model Weights + KV Cache + Activations + Overhead

FP16 estimate:
  params (billions) × 2 = weight VRAM (GB)
  e.g., 13B model → 13 × 2 = 26 GB weights alone
```

### Gotchas & Dev Context
- **Rule of thumb**: FP16 → 2 GB/B params; INT8 → 1 GB/B; INT4 → 0.5 GB/B
- KV cache grows with batch size × sequence length — it can dominate VRAM at scale
- Always add 20% overhead buffer for activations and framework overhead
- Multi-GPU tensor parallelism splits weight VRAM linearly across GPUs
- Tools: `model.get_memory_footprint()` in HuggingFace, `nvidia-smi`, vLLM's `--gpu-memory-utilization` flag
- Gradient memory (for training) ≈ 4–6× inference memory — don't confuse the two

### Production FAQ
**Q: My model fits in VRAM alone but OOMs during inference. Why?**
A: KV cache or activation spikes. Reduce batch size or max sequence length, or enable KV cache offloading.

**Q: How do I split a model across 2 GPUs?**
A: Use `device_map="auto"` in HuggingFace Accelerate, or tensor parallelism in vLLM.

**Q: What's the cheapest cloud GPU for a 7B model at INT4?**
A: ~3.5 GB for weights. An RTX 3080 (10 GB) or AWS `g4dn.xlarge` (T4, 16 GB) handles it comfortably.

---

## 14. CPU vs GPU vs TPU Inference

### Definition
Three compute paradigms for running ML models — each with different speed, cost, and accessibility tradeoffs.

### Real-World Dev Example
A startup with no GPU budget runs a distilled BERT model on CPU (2 req/sec). A scale-up uses a single A10 GPU (200 req/sec). A hyperscaler uses Google TPUs for millions of requests/day.

### ASCII Diagram
```
         CPU              GPU               TPU
Speed    Slow (ms–s)      Fast (ms)         Fastest (µs–ms)
Cost     Cheap            Medium–High       High (GCP only)
Parallel Low (cores)      High (1000s cuda) Extreme (matrix ops)
Setup    Zero             CUDA drivers      GCP TPU pod only
Best for Tiny models,     Most prod models  Google-scale LLMs
         edge/CPU-only    & fine-tuning
```

### Gotchas & Dev Context
- CPU inference is viable for small models (<100M params) with ONNX Runtime
- GPUs have "memory bandwidth" bottlenecks for LLMs, not just FLOPS
- TPUs require XLA compilation — incompatible with arbitrary PyTorch ops
- Apple Silicon (M-series) MPS backend is a strong CPU+GPU hybrid for Mac deployments
- For cost-sensitivity: CPUs at scale can beat GPU spot instances for low-throughput APIs

### Production FAQ
**Q: When should I use CPU inference in production?**
A: For lightweight NLP tasks (<100M params), batch jobs without SLA, or when GPU cost is prohibitive.

**Q: Can I switch from GPU to TPU easily?**
A: No — TPU requires JAX or TPU-compatible TensorFlow. It's a significant engineering investment.

**Q: Is Apple's M2/M3 GPU good for inference?**
A: Yes — unified memory makes 70B models feasible locally via `llama.cpp`. Not for high-concurrency serving.

---

## 15. Edge Inference (ONNX Runtime, TFLite)

### Definition
Running ML models directly on device (phone, IoT sensor, laptop) without sending data to a server — enabling offline, low-latency, and privacy-preserving AI.

### Real-World Dev Example
A mobile app detects objects in camera frames using a MobileNet model converted to TFLite — running at 30 FPS on-device with no internet connection.

### ASCII Diagram
```
Cloud Inference:              Edge Inference:
Photo → [Internet] → Server   Photo → [On-device Model]
     → Result (latency: 200ms)      → Result (latency: 10ms)
     (privacy risk, needs wifi)      (offline, private)
```

### Gotchas & Dev Context
- **ONNX Runtime** — runs on Windows/Linux/Android/iOS; broad hardware support
- **TFLite** — Android/iOS/microcontrollers; tighter Google ecosystem
- Models must be quantized (INT8/INT4) for edge — full FP32 won't fit on device
- Benchmark on target hardware — desktop benchmarks don't transfer
- TFLite supports hardware delegation: GPU Delegate, NNAPI, Hexagon DSP
- Core ML (Apple) and TensorFlow Lite are the dominant mobile runtimes
- Model size budget: ~50 MB for mobile apps (APK/IPA size constraints)

### Production FAQ
**Q: How do I convert a PyTorch model for edge deployment?**
A: PyTorch → ONNX → ONNX Runtime Mobile, or PyTorch → TorchScript → (converter) → TFLite.

**Q: Can LLMs run on edge devices?**
A: Small ones (1–3B, INT4) can run on high-end phones. Tools: `llama.cpp`, `MLC LLM`, `Ollama`.

**Q: What if my model is too large for edge?**
A: Distill (§3) + quantize (§1) until it fits, or split compute between edge and cloud.

---

## 16. Model Caching / Warm Start

### Definition
Keeping a model loaded in memory between requests (warm) instead of loading it fresh each time (cold start) — eliminating multi-second startup delays in production.

### Real-World Dev Example
An AWS Lambda function that loads a 500 MB model on every invocation takes 8 seconds cold. With provisioned concurrency (warm instances), response time drops to 80ms.

### ASCII Diagram
```
Cold Start:
Request → [Load model from disk: 5s] → [Inference: 80ms] → Response
                   ↑ Terrible UX

Warm Start:
Request → [Model already in RAM] → [Inference: 80ms] → Response
                   ↑ Great UX
```

### Gotchas & Dev Context
- Warm-up request (send a dummy input on startup) pre-compiles CUDA kernels
- KV cache caching (prefix caching) in vLLM saves recomputing repeated system prompts
- Serverless functions (Lambda, Cloud Run) suffer cold starts — use min-instances or dedicated servers
- Model files should be stored on fast NVMe SSD — network-mounted volumes add 10–30s cold starts
- Multi-model serving: use LRU eviction to manage which models stay warm
- Prometheus metric to watch: `model_load_time_seconds`

### Production FAQ
**Q: How do I force a warm start in Kubernetes?**
A: Use `readinessProbe` that sends a dummy request, and set `minReadySeconds`. Keep replicas ≥ 1 always running.

**Q: What's prefix caching in vLLM?**
A: If multiple requests share the same system prompt, vLLM caches those KV states — skipping re-computation and saving significant time.

**Q: Should I cache model outputs too?**
A: Yes, for deterministic or repeated queries. Use Redis with a hash of (model_id + input) as the cache key.

---

## 17. Streaming Responses

### Definition
Sending model output to the client token-by-token as it's generated, rather than waiting for the full response — creating a responsive, ChatGPT-like typing experience.

### Real-World Dev Example
A legal summarization tool processes 5,000-word documents. Without streaming, users wait 30 seconds for the full output. With streaming, they see the first words in under a second.

### ASCII Diagram
```
Without Streaming:
Model generates: [tok1 tok2 tok3 ... tok200]
Client receives: ████████████████████████ → [Full response at t=30s]

With Streaming:
Model generates: tok1 → tok2 → tok3 → ...
Client receives:  t↑    t↑    t↑    → Visible typing effect
```

### Gotchas & Dev Context
- Implemented via **Server-Sent Events (SSE)** or **WebSockets** — SSE is simpler for one-way streaming
- OpenAI API uses `stream=True`; vLLM/TGI support it natively
- Streaming doesn't reduce total generation time — it only improves perceived latency
- Clients must handle chunked HTTP responses; not all reverse proxies buffer correctly (check nginx `proxy_buffering off`)
- Error handling is harder — you've already streamed partial output before detecting a failure
- Token-by-token streaming has slightly higher CPU overhead than batched delivery

```python
# OpenAI-style streaming
for chunk in client.chat.completions.create(..., stream=True):
    print(chunk.choices[0].delta.content or "", end="", flush=True)
```

### Production FAQ
**Q: Does streaming work with all LLM serving frameworks?**
A: Yes — vLLM, TGI, Triton (with custom backend), BentoML, and LiteLLM all support SSE streaming.

**Q: How do I handle streaming in a mobile app?**
A: Use an HTTP client that supports chunked transfer encoding (OkHttp on Android, URLSession on iOS).

**Q: Can I cancel a streaming response mid-way?**
A: Yes — close the HTTP connection from the client. Configure your server to detect disconnect and stop generation (vLLM does this automatically).
