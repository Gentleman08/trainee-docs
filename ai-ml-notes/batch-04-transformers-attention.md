# Batch 4 — Transformers & Attention
> The architecture that changed everything — from BERT to GPT to modern LLMs.

---

## 1. Attention Mechanism

### Definition
A technique that lets a model focus on the most relevant parts of the input when producing each output token — instead of compressing everything into one fixed vector.

### Real-World Dev Example
Machine translation: when translating "The bank by the river," the model attends more to "river" to resolve that "bank" = riverbank, not financial institution.

### ASCII Diagram
```
Input tokens:  [The]  [bank]  [by]  [the]  [river]
                                              ↑
                    Attention weights ────────┘
                    (bank strongly attends to "river")
```

### Gotchas & Dev Context
- Pre-attention RNNs had a **bottleneck**: all meaning had to pass through one hidden state
- Attention scores are raw logits — they're **softmax'd** to sum to 1 (so they're a probability distribution over tokens)
- Attention is **O(n²)** in sequence length — this becomes costly for very long inputs
- "Soft attention" = weighted average over all positions; "hard attention" = picks one (rarely used)

### Production FAQ
**Q: Does attention replace the need for memory in RNNs?**
A: Yes — attention gives direct access to all previous positions, so there's no vanishing-gradient bottleneck over long sequences.

**Q: Is attention only used in NLP?**
A: No. Vision Transformers (ViT) apply attention to image patches. It's now universal across modalities.

---

## 2. Self-Attention

### Definition
A special case of attention where a sequence attends to **itself** — every token looks at every other token in the same sequence to build context-aware representations.

### Real-World Dev Example
In the sentence "It picked up the ball and threw **it**," self-attention lets the model resolve that the second "it" refers to "ball" by learning high attention weights between them.

### ASCII Diagram
```
Each token produces Q, K, V vectors:

Token: "threw"
  Q ──► dot product with all K's ──► softmax ──► weighted sum of V's
                                          ↑
                             (attends heavily to "it", "ball")
```

### Gotchas & Dev Context
- Every token has three learned projections: **Query (Q)**, **Key (K)**, **Value (V)**
- Score = `softmax(QKᵀ / √d_k) · V` — the `√d_k` prevents vanishing gradients from large dot products
- Self-attention is **permutation invariant** — that's why positional encodings are needed
- Computationally symmetric: token A attending to B gives the same cost as B attending to A

### Production FAQ
**Q: What's the difference between self-attention and cross-attention?**
A: Self-attention: Q, K, V all come from the same sequence. Cross-attention: Q comes from the decoder, K and V come from the encoder output.

**Q: Why divide by √d_k?**
A: Large d_k causes dot products to grow large → softmax saturates → near-zero gradients. Scaling keeps them in a healthy range.

---

## 3. Multi-Head Attention

### Definition
Running self-attention **multiple times in parallel** with different learned projections, then concatenating the results — so the model can attend to different types of relationships simultaneously.

### Real-World Dev Example
For "John gave Mary his book," one head might capture subject-verb agreement (John→gave), another coreference (his→John), another object relationships (gave→book) — all at once.

### ASCII Diagram
```
Input X
  ├── Head 1: Q₁K₁V₁ ──► output₁ ─┐
  ├── Head 2: Q₂K₂V₂ ──► output₂ ─┼──► Concat ──► Linear ──► Output
  └── Head N: QₙKₙVₙ ──► outputₙ ─┘
```

### Gotchas & Dev Context
- Each head uses **reduced dimension** (d_model / num_heads), so total cost ≈ single full-size attention
- Typical configs: GPT-2 uses 12 heads; GPT-3 uses 96 heads
- Different heads don't always learn distinct roles — they can be redundant; some pruning research exploits this
- The final linear projection fuses information across heads

### Production FAQ
**Q: How many attention heads should I use?**
A: Convention is `num_heads = d_model / 64`. So for d_model=768, use 12 heads. This isn't strict — experiment for your task.

**Q: Can I use fewer heads to speed up inference?**
A: Yes. Head pruning (removing low-importance heads) can cut compute with minimal accuracy loss — common in model compression pipelines.

---

## 4. Transformer Architecture

### Definition
A deep learning architecture built entirely on attention (no RNNs, no convolutions) that processes all tokens in parallel and has become the foundation of modern NLP and beyond.

### Real-World Dev Example
GPT, BERT, T5, Whisper, ViT — all are Transformers. When you call `openai.chat.completions.create(...)`, you're running a Transformer under the hood.

### ASCII Diagram
```
Encoder Block (×N):               Decoder Block (×N):
┌──────────────────┐              ┌──────────────────────┐
│ Multi-Head Attn  │              │ Masked Multi-Head Attn│
│ + Add & Norm     │              │ + Add & Norm          │
│ Feed-Forward     │──► Memory ──►│ Cross-Attention       │
│ + Add & Norm     │              │ + Add & Norm          │
└──────────────────┘              │ Feed-Forward          │
                                  │ + Add & Norm          │
                                  └──────────────────────┘
```

### Gotchas & Dev Context
- **Residual connections** (Add) prevent vanishing gradients in deep stacks
- **Layer Norm** stabilizes training; applied before (Pre-LN) or after (Post-LN) attention
- Feed-forward layers use ~4× hidden dimension expansion (e.g., 768 → 3072 → 768)
- Decoder-only (GPT style) vs Encoder-only (BERT style) vs Full Enc-Dec (T5 style)

### Production FAQ
**Q: Why does the Transformer outperform RNNs on long sequences?**
A: RNNs process tokens sequentially — gradients degrade over distance. Transformers have direct token-to-token paths with constant gradient flow.

**Q: What's the Feed-Forward layer doing?**
A: It applies a position-wise MLP — storing factual associations and acting as a "memory" per token, complementing what attention does for context mixing.

---

## 5. Positional Encoding / Positional Embeddings

### Definition
A signal added to token embeddings to inject information about **token order**, since self-attention itself is order-blind (permutation invariant).

### Real-World Dev Example
"Dog bites man" vs "Man bites dog" — same tokens, different meaning. Without positional info, the Transformer can't distinguish them.

### ASCII Diagram
```
Token Embedding:    [0.2, 0.8, -0.1, ...]
Positional Signal:  [0.0, 1.0,  0.0, ...]  ← for position 3
                  +
Final Input:        [0.2, 1.8, -0.1, ...]
```

### Gotchas & Dev Context
- **Sinusoidal (original paper)**: fixed math formula using sin/cos at different frequencies — no learned params, generalizes to unseen lengths
- **Learned absolute** (BERT, GPT-2): a lookup table per position — simple but can't extrapolate beyond training length
- **RoPE (Rotary Position Embedding)**: used in LLaMA, GPT-NeoX — rotates Q/K vectors by position angle, handles long contexts better
- **ALiBi**: adds a position bias to attention scores — no embedding needed, extrapolates cleanly

### Production FAQ
**Q: Can a model generalize to sequences longer than it was trained on?**
A: With learned absolute embeddings — usually not. RoPE and ALiBi handle this much better, which is why modern LLMs use them.

**Q: Do I need positional encodings for all Transformer tasks?**
A: For order-sensitive tasks (text, audio, time series) — yes. For unordered sets (some graph tasks) — you might omit them intentionally.

---

## 6. Encoder-Decoder Architecture

### Definition
A Transformer design with two components: an **encoder** that reads and understands the full input, and a **decoder** that generates the output one token at a time using cross-attention into the encoder.

### Real-World Dev Example
Translation: the encoder reads the French sentence, builds rich representations, then the decoder attends to those representations while generating English tokens word by word.

### ASCII Diagram
```
Source: "Bonjour monde"
         │
    [Encoder ×N]  ──────────────────────────────┐
         │                                       │ (memory / encoder output)
    [Compressed Representations]                 ↓
                                          [Decoder ×N]
                                          ↑ cross-attention
                                          "Hello world" (generated)
```

### Gotchas & Dev Context
- Cross-attention: decoder's Q attends to encoder's K and V
- Decoder is **autoregressive** — generates one token, feeds it back as input for the next
- T5, BART, MarianMT use this design
- Encoder-only (BERT) = better for understanding tasks; Decoder-only (GPT) = better for generation
- Enc-Dec = flexible but heavier than decoder-only for pure generation

### Production FAQ
**Q: When should I use Enc-Dec vs Decoder-only?**
A: Enc-Dec excels at input→output transformation (translation, summarization). Decoder-only is preferred for open-ended generation and scales better to huge sizes.

**Q: Is cross-attention expensive?**
A: It's proportional to `len(source) × len(target)` — manageable for typical tasks, but long-document summarization can be costly.

---

## 7. BERT (Bidirectional Encoder Representations from Transformers)

### Definition
An encoder-only Transformer pre-trained to predict masked tokens using **both left and right context** — producing rich, bidirectional representations for NLP understanding tasks.

### Real-World Dev Example
Fine-tune BERT on labeled support tickets to classify them as Bug / Feature Request / Question — achieving high accuracy with minimal training data.

```python
from transformers import BertForSequenceClassification
model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=3)
```

### Gotchas & Dev Context
- Pre-training task: **Masked Language Model (MLM)** — 15% of tokens are masked; model predicts them
- Second task: **Next Sentence Prediction (NSP)** — later research (RoBERTa) showed NSP adds little value
- BERT is **not autoregressive** — can't generate text; use it for classification, NER, QA, embeddings
- `bert-base`: 110M params, 12 layers, 12 heads; `bert-large`: 340M params, 24 layers, 16 heads
- Input format: `[CLS] sentence A [SEP] sentence B [SEP]`

### Production FAQ
**Q: Should I still use BERT in 2024/2025?**
A: For classification, NER, and embedding tasks on CPU/edge — yes, it's fast and well-understood. For generation, use GPT-family instead.

**Q: What's the `[CLS]` token for?**
A: It's a special token whose final hidden state aggregates sentence-level representation — used as input to the classification head.

---

## 8. GPT (Generative Pre-trained Transformer)

### Definition
A **decoder-only** Transformer trained to predict the next token given all previous tokens — enabling open-ended text generation and the backbone of ChatGPT, Copilot, and most modern LLMs.

### Real-World Dev Example
GitHub Copilot uses a GPT-family model: given your function signature and docstring, it autoregressively predicts the most likely implementation tokens.

### ASCII Diagram
```
Prompt: "def add(a, b):"
  ↓
[Token 1] → [Token 2] → [Token 3] → ... → [return a + b]
  Each token can only attend to tokens to its LEFT (causal mask)
```

### Gotchas & Dev Context
- Uses **causal (masked) self-attention** — each token only sees past tokens, never future ones
- GPT-1: 117M params; GPT-2: 1.5B; GPT-3: 175B; GPT-4: estimated ~1T (MoE)
- Pre-training objective is simple: maximize `P(token_t | token_1, ..., token_{t-1})`
- Fine-tuning approaches: full fine-tune, LoRA, RLHF (for instruction following)
- **Temperature** controls randomness at inference; top-p/top-k control vocabulary sampling

### Production FAQ
**Q: Can GPT do classification like BERT?**
A: Yes — via prompting or adding a classification head. But BERT-style models are still more efficient for pure classification tasks.

**Q: Why can't GPT see future tokens during training?**
A: The model must learn to predict them — seeing them would be "cheating" and prevent learning a useful generative distribution.

---

## 9. T5 (Text-to-Text Transfer Transformer)

### Definition
A full encoder-decoder Transformer that frames **every NLP task as text-in → text-out**, using a unified format for translation, summarization, classification, and QA.

### Real-World Dev Example
Instead of separate models for each task, T5 takes: `"summarize: [article text]"` → outputs the summary. Same model, same format for translation: `"translate English to German: Hello"`.

### ASCII Diagram
```
Input:  "classify sentiment: I love this product"
         │
    [Encoder] ──────── [Decoder]
                            │
Output: "positive"
```

### Gotchas & Dev Context
- Pre-trained on **C4** (Colossal Clean Crawled Corpus) with a **span-corruption** objective (not single-token masking)
- Task prefix (e.g., `"summarize:"`) is critical — the model is prefix-conditioned
- T5-small: 60M params → T5-11B: 11B params; Flan-T5 adds instruction tuning
- Unlike GPT, T5 can look at the **full input** bidirectionally before generating output
- Good for structured generation: slot filling, code generation, structured QA

### Production FAQ
**Q: When is T5 better than GPT for production?**
A: For tasks with clear input→output structure (translation, summarization, classification), T5 trains more efficiently and performs competitively with smaller models.

**Q: Do I need to include the task prefix at inference?**
A: Yes — omitting it causes the model to produce garbage. Always match the exact prefix format used during fine-tuning.

---

## 10. Tokenization (BPE, WordPiece, SentencePiece)

### Definition
The process of splitting raw text into **tokens** (sub-words, characters, or words) that map to integer IDs — the bridge between text and model input.

### Real-World Dev Example
`"unhappiness"` → `["un", "happiness"]` (WordPiece) or `["un", "hap", "pi", "ness"]` (BPE), depending on vocabulary. Each gets an integer ID fed into the embedding layer.

### Gotchas & Dev Context
- **BPE (Byte-Pair Encoding)**: merges the most frequent character pairs iteratively — used by GPT-2, RoBERTa, LLaMA
- **WordPiece**: similar to BPE but merges based on likelihood increase — used by BERT
- **SentencePiece**: language-agnostic, treats text as raw bytes (no pre-tokenization) — used by T5, LLaMA 2+
- Token count ≠ word count: `"ChatGPT"` may be 3 tokens; emojis can be 3–6 tokens
- Vocabulary size trade-off: too small → long sequences; too large → sparse embeddings
- Rare languages are often over-tokenized (more tokens per word), causing worse performance

### Production FAQ
**Q: Can I use a custom tokenizer for my domain (e.g., medical, legal)?**
A: Yes — train BPE/SentencePiece on your corpus to reduce token fragmentation for domain-specific vocabulary. Requires retraining the embedding layer.

**Q: Why does token count matter for API costs?**
A: Most LLM APIs (OpenAI, Anthropic) bill per token. `tiktoken` lets you count tokens before sending to avoid surprises.

---

## 11. Embeddings (Word2Vec, GloVe, FastText)

### Definition
Dense vector representations of words that encode semantic meaning — similar words cluster together in vector space, enabling math-like operations on language.

### Real-World Dev Example
`king - man + woman ≈ queen` — the classic Word2Vec analogy. In practice: use pre-trained embeddings to initialize a text classifier, reducing labeled data needs.

### ASCII Diagram
```
Word space (2D projection):
  "dog" •                    • "cat"
        • "puppy"      • "kitten"

         Semantic similarity = cosine distance
```

### Gotchas & Dev Context
- **Word2Vec**: two training methods — Skip-Gram (predict context from word) and CBOW (predict word from context)
- **GloVe**: uses global co-occurrence matrix statistics — often slightly better on analogies
- **FastText**: represents words as bags of character n-grams → handles OOV (out-of-vocabulary) words
- All three are **static** — "bank" has the same vector regardless of context (river vs. financial)
- These are largely superseded by contextual embeddings for NLP, but still useful for fast similarity search, recommendation systems, and low-resource scenarios

### Production FAQ
**Q: Should I still use Word2Vec in 2025?**
A: For recommendation systems, fast semantic search, or when you need lightweight embeddings — yes. For NLP tasks where context matters — use contextual embeddings instead.

**Q: How do I handle words not in my vocabulary?**
A: Use FastText (subword-aware) or map OOV to `<UNK>`. With modern tokenizers + contextual models, OOV is essentially eliminated.

---

## 12. Contextual Embeddings

### Definition
Word representations that **change based on surrounding context** — the same word gets a different vector in different sentences, capturing polysemy and nuance.

### Real-World Dev Example
`"Apple"` in "I ate an apple" → embedding clusters near fruit. `"Apple"` in "Apple released iOS 18" → embedding clusters near tech companies. BERT produces different vectors for each.

### ASCII Diagram
```
Static:     "bank" ──► [0.2, 0.7, -0.3]  (always same)

Contextual: "bank" in "river bank" ──► [0.1, 0.9, -0.5]
            "bank" in "bank transfer" ──► [0.8, 0.1,  0.6]
```

### Gotchas & Dev Context
- Produced by the **hidden states** of Transformer models (BERT, GPT, etc.)
- Common practice: use the last hidden state or a mean-pool of all hidden states as a sentence embedding
- **Sentence-BERT (SBERT)**: fine-tunes BERT with siamese networks to produce useful sentence-level embeddings for similarity tasks
- Dimension matters: BERT-base → 768-dim; larger models → up to 4096-dim
- For semantic search pipelines (RAG), contextual embeddings dramatically outperform static ones

### Production FAQ
**Q: Which layer's embeddings should I extract?**
A: For semantic similarity — penultimate or last layer. For syntax/structure — earlier layers. Many tasks benefit from averaging all layers (ELMo-style).

**Q: Can I use GPT embeddings for similarity search?**
A: Yes — OpenAI's `text-embedding-ada-002` / `text-embedding-3` are optimized for this. They're GPT-based and work well out of the box for RAG pipelines.

---

## 13. Causal / Masked Language Modeling

### Definition
Two pre-training objectives: **Masked LM (MLM)** predicts randomly hidden tokens using full context (BERT-style); **Causal LM (CLM)** predicts the next token using only past tokens (GPT-style).

### Real-World Dev Example
- MLM: `"The [MASK] sat on the mat"` → model predicts `"cat"` using left AND right context
- CLM: `"The cat sat on the"` → model predicts `"mat"` using only left context

### ASCII Diagram
```
MLM (Bidirectional):
← ← [MASK] → →     All tokens inform the prediction

CLM (Causal/Left-to-right):
[The] [cat] [sat] → predict [on]
 ✓     ✓     ✓         ✗ (future tokens blocked)
```

### Gotchas & Dev Context
- CLM enables **generation** naturally — just keep sampling the next token
- MLM produces richer contextual representations but **cannot generate** autoregressively
- **Prefix LM** (used in T5's decoder, UniLM): full attention on prefix, causal attention on the generated part — best of both worlds
- BERT's 15% masking rate is a deliberate sweet spot — too high = too hard; too low = too little signal

### Production FAQ
**Q: Why can't I use a BERT model to generate text?**
A: BERT's masked attention allows all positions to see all others — there's no causal constraint, so it can't generate one token at a time without seeing future tokens it hasn't generated yet.

**Q: Is CLM less data-efficient than MLM?**
A: Yes — CLM only predicts one token per position; MLM predicts ~15% of them simultaneously. But CLM's emergent generation ability makes it worth the trade-off at scale.

---

## 14. Sequence Length / Context Window

### Definition
The maximum number of tokens a model can process in a single forward pass — tokens beyond this limit are simply cut off and invisible to the model.

### Real-World Dev Example
GPT-3.5 has a 4K context window. Feeding a 10K-token legal document means the model only sees the last 4K tokens — the first 6K are silently ignored, potentially missing crucial clauses.

### Gotchas & Dev Context
- Context window = prompt tokens + completion tokens combined (for most APIs)
- Attention is **O(n²)** in memory and compute — doubling context length quadruples attention cost
- Modern context lengths: GPT-4: 128K, Claude 3: 200K, Gemini 1.5: 1M tokens
- Long context ≠ perfect recall — "lost in the middle" problem: models perform worse on info in the middle of very long contexts
- Techniques to extend context: RoPE interpolation, ALiBi, sliding window attention, retrieval (RAG)

### Production FAQ
**Q: If I have a 128K context model, should I always max it out?**
A: No. Longer context = more latency and higher cost. Use retrieval (RAG) to fetch only relevant chunks instead of stuffing everything in.

**Q: What happens when I exceed the context window?**
A: Most APIs/frameworks silently truncate from the **beginning** of the input. Always track token counts explicitly using a tokenizer.

---

## 15. KV Cache

### Definition
A memory optimization that **stores the Key and Value matrices** from previously generated tokens so they don't need to be recomputed on every autoregressive generation step.

### Real-World Dev Example
Generating a 500-token response: without KV cache, every new token requires reprocessing all 499 previous tokens. With KV cache, each step only computes K/V for the one new token.

### ASCII Diagram
```
Without KV Cache:
Step 3: recompute K,V for [tok1, tok2, tok3] → slow

With KV Cache:
Step 3: load cached K,V for [tok1, tok2], compute only [tok3] → fast
         └───── stored from previous steps ──────┘
```

### Gotchas & Dev Context
- KV cache size grows linearly with sequence length and batch size — the #1 cause of OOM errors in LLM serving
- Cache size = `2 × num_layers × num_heads × head_dim × seq_len × bytes_per_param`
- For a 70B model with 4K context and batch=32 → cache can be **tens of GBs**
- **Multi-Query Attention (MQA)** and **Grouped-Query Attention (GQA)** (used in LLaMA 2/3, Mistral) reduce KV cache size by sharing K/V heads across query heads
- Quantizing KV cache (fp8, int8) is a common production optimization

### Production FAQ
**Q: Does KV cache persist across API calls?**
A: Not by default. Most APIs rebuild the cache per request. Prompt caching (Anthropic, OpenAI) is an emerging feature that does persist it for repeated prefixes.

**Q: How does KV cache affect throughput vs latency?**
A: It drastically improves **latency** (faster per-token generation). Throughput is limited by GPU memory available for the cache — larger batches compete for cache space.

---

## 16. Flash Attention

### Definition
A hardware-aware algorithm that rewrites standard attention to **minimize memory reads/writes between GPU HBM and SRAM**, making attention significantly faster and more memory-efficient without changing the mathematical result.

### Real-World Dev Example
Training a 7B model on 4K-length sequences with standard attention hits OOM on an A100. With FlashAttention-2, the same training runs smoothly — same outputs, ~2-4× faster.

### ASCII Diagram
```
Standard Attention:
GPU HBM → load Q,K,V → compute scores (full N×N matrix) → write to HBM → load back → compute output

Flash Attention:
GPU HBM → load small TILE of Q,K,V → compute + accumulate in SRAM → write final output
          (never materializes the full N×N attention matrix in HBM)
```

### Gotchas & Dev Context
- Mathematically **identical** to standard attention — it's an implementation trick, not an approximation
- Reduces memory from O(n²) to O(n) — enabling much longer sequences on the same hardware
- FlashAttention-2 introduced better parallelism; FlashAttention-3 targets H100/Hopper architecture
- Available in PyTorch (`F.scaled_dot_product_attention`) automatically on modern versions
- Doesn't help CPU inference — purely a GPU optimization (SRAM/HBM hierarchy)

### Production FAQ
**Q: Do I need to change my model code to use FlashAttention?**
A: Often no. Hugging Face Transformers and PyTorch >= 2.0 use it automatically via `torch.nn.functional.scaled_dot_product_attention`. Pass `attn_implementation="flash_attention_2"` in some HF models.

**Q: Does FlashAttention improve output quality?**
A: No — results are numerically identical to standard attention (within floating point precision). It's a pure efficiency gain.

---

## 17. Mixture of Experts (MoE)

### Definition
An architecture where the model is split into many specialized sub-networks ("experts"), and for each token, a **router** selects only a small subset of experts to activate — scaling capacity without scaling compute proportionally.

### Real-World Dev Example
Mixtral 8×7B: 8 expert FFN layers per block, but only 2 are active per token. Total params: ~46B, but compute per token ≈ a 12B dense model. GPT-4 is rumored to use MoE with ~8 experts.

### ASCII Diagram
```
Token → [Router] → selects Top-2 experts
           │
    ┌──────┴──────┐
   [Expert 1]  [Expert 3]   ← only these 2 fire
   [Expert 2]  [Expert 4]   ← dormant for this token
   ...         ...
           │
    Weighted sum of expert outputs
```

### Gotchas & Dev Context
- **Load balancing** is critical — if all tokens route to Expert 1, others go unused; auxiliary loss is added to encourage balance
- MoE models have high **parameter count but low active compute** — great for quality, but all params must fit in GPU memory
- Expert parallelism: distribute experts across GPUs — each GPU hosts different experts
- "Dead expert" problem: some experts receive no gradient and stop learning
- MoE is most effective at very large scales; smaller MoE models often underperform equivalent dense models

### Production FAQ
**Q: Is a 46B MoE model cheaper to run than a 46B dense model?**
A: Yes — significantly. Active compute matches a ~12B model. But you need enough GPU memory to hold all 46B parameters.

**Q: Why not activate more experts for better quality?**
A: Each extra active expert adds proportional compute. The sparsity (top-2 of 8) is the whole point — it's a compute-quality trade-off.

---

## 18. Scaling Laws (Chinchilla, Kaplan)

### Definition
Empirical rules that describe how model **loss improves predictably** as you scale model size, dataset size, and compute — guiding efficient allocation of training resources.

### Real-World Dev Example
Before Chinchilla: everyone scaled model params (GPT-3: 175B params, ~300B tokens). After Chinchilla: Mistral-7B trained on trillions of tokens beats models 10× its size, because data was the bottleneck.

### ASCII Diagram
```
Loss
 │  \
 │   \   Kaplan: scale N (params) aggressively
 │    \___
 │        \____ Chinchilla: N and D (tokens) should scale together
 └────────────────────────────────────────►
              Compute Budget
```

### Gotchas & Dev Context
- **Kaplan et al. (2020)**: loss ∝ N^(-0.076) and D^(-0.095) — suggested scaling params > data
- **Chinchilla (Hoffmann et al., 2022)**: optimal training uses **~20 tokens per parameter** (e.g., 70B model → 1.4T tokens)
- Chinchilla showed GPT-3 was "undertrained" — same compute budget, smaller model + more data = better results
- Scaling laws describe **pre-training loss**, not downstream task performance — task-specific behavior can break the trend
- LLaMA models pushed this further: train smaller models on far more tokens → better inference efficiency

### Production FAQ
**Q: If scaling laws are smooth, why do emergent abilities appear suddenly?**
A: Scaling laws govern average loss — emergent abilities appear when loss crosses a threshold for specific tasks. The underlying improvement is smooth; task success is not.

**Q: Does Chinchilla apply to fine-tuning?**
A: No — Chinchilla governs pre-training compute allocation. Fine-tuning dynamics follow different rules (fewer steps, lower LR, smaller data).
