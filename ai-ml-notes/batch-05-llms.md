# Batch 5 — Large Language Models (LLMs)
> How GPT, Claude, and Gemini actually work — and how to build with them responsibly.

---

## 1. LLM (Large Language Model)

### Definition
A neural network trained on massive text corpora to predict and generate human-like text. "Large" refers to both the dataset size and the billions of parameters that store learned knowledge.

### Real-World Dev Example
You call `openai.chat.completions.create(model="gpt-4o", messages=[...])` and the model writes a SQL query from a plain-English description — that's an LLM in production.

### ASCII Diagram
```
Input tokens → [Transformer Layers × N] → Output token probabilities → Sampled token
                      ↑
             (attention + FFN blocks)
```

### Gotchas & Dev Context
- LLMs don't "know" facts — they predict plausible continuations; accuracy isn't guaranteed
- Cost scales with token count, not response quality
- Model weights are frozen at inference — they can't learn new info on the fly
- Latency is dominated by output token generation (auto-regressive, one token at a time)

### Production FAQ
**Q: Can I use an LLM offline?**
A: Yes — open-source models (Llama, Mistral) can run locally via `ollama` or `llama.cpp`, trading cloud cost for hardware requirements.

**Q: Why do two identical prompts sometimes give different answers?**
A: Temperature > 0 introduces randomness in token sampling. Set `temperature=0` for deterministic outputs.

---

## 2. Foundation Model

### Definition
A large model pre-trained on broad, general data that can be adapted to many downstream tasks — the "base" that specialized models are built on top of.

### Real-World Dev Example
GPT-4 is a foundation model. A company fine-tunes it on their legal documents to create a contract-review assistant — same base, specialized behavior.

### ASCII Diagram
```
           [Foundation Model]
                  │
    ┌─────────────┼─────────────┐
    ▼             ▼             ▼
 Code Gen     Medical QA    Chatbot
(fine-tuned) (fine-tuned)  (prompted)
```

### Gotchas & Dev Context
- Foundation models embed societal biases present in web-scale training data
- They're expensive to train (millions of dollars); most teams never train one from scratch
- "Foundation model" ≠ always open-source — GPT-4 weights are closed
- Multimodal foundation models (GPT-4o, Gemini) accept text + images + audio

### Production FAQ
**Q: Should I fine-tune a foundation model or just prompt it?**
A: Prompt first — it's faster and cheaper. Fine-tune only when prompting consistently fails to hit quality targets.

**Q: Who owns the outputs of a foundation model?**
A: Depends on the provider's ToS and your jurisdiction. OpenAI currently grants users ownership of outputs; always verify per-use-case.

---

## 3. Pre-training vs Fine-tuning

### Definition
**Pre-training** is initial training on massive unlabeled text to build general language understanding. **Fine-tuning** is additional, targeted training on a smaller labeled dataset to adapt the model to a specific task or style.

### Real-World Dev Example
OpenAI pre-trains GPT-4 on internet-scale text (pre-training), then trains it further on instruction-following examples and human preference data (fine-tuning) to produce ChatGPT.

### ASCII Diagram
```
Web-scale text (TB)                   Task dataset (MB–GB)
      │                                        │
      ▼                                        ▼
[Pre-training: weeks/months]     [Fine-tuning: hours/days]
      │                                        │
  Base model ──────────────────────────► Fine-tuned model
```

### Gotchas & Dev Context
- Pre-training costs millions in compute — never done by most teams
- Fine-tuning can cause **catastrophic forgetting** (model forgets general knowledge)
- Parameter-Efficient Fine-Tuning (PEFT/LoRA) reduces fine-tuning cost dramatically
- Fine-tuned models still hallucinate — it's not a silver bullet for accuracy

### Production FAQ
**Q: When is fine-tuning worth it over prompting?**
A: When you need a consistent tone/format, domain-specific vocabulary, or the task requires dozens of examples in the prompt that bloat cost.

**Q: How much data do I need to fine-tune?**
A: As few as 50–500 high-quality examples can meaningfully shift behavior. Quality beats quantity.

---

## 4. Transfer Learning

### Definition
Reusing knowledge a model gained during training on one task to help it perform better on a different but related task — avoiding training from scratch.

### Real-World Dev Example
A sentiment analysis model fine-tuned from BERT (pre-trained on Wikipedia) reaches 92% accuracy with only 1,000 labeled examples — far fewer than training from scratch would need.

### ASCII Diagram
```
[Pre-trained weights: general knowledge]
            │
            │  (freeze most layers, retrain top layers)
            ▼
[Fine-tuned weights: task-specific knowledge]
```

### Gotchas & Dev Context
- The source and target tasks must share some structure — transferring an English model to code works; transferring it to protein sequences may not
- More layers frozen = faster training, less adaptation; fewer frozen = slower but more flexible
- Transfer learning is why LLMs work so well — language understanding transfers broadly
- Domain shift (e.g., medical jargon) can limit how much transfers

### Production FAQ
**Q: Is using an LLM API an example of transfer learning?**
A: Conceptually yes — you're leveraging pre-trained knowledge via prompting. Technically, transfer learning usually implies updating weights, not just inference.

**Q: Does transfer learning always improve performance?**
A: Usually, but not always. If the domains are too dissimilar, pre-trained weights can hurt (negative transfer).

---

## 5. Instruction Tuning

### Definition
A fine-tuning technique where a base model is trained on (instruction → response) pairs, teaching it to follow natural-language commands rather than just complete text.

### Real-World Dev Example
A base GPT model might complete "Write a haiku about..." by adding more poetry. After instruction tuning, it recognizes the instruction and writes exactly one haiku on-topic.

### ASCII Diagram
```
Base model (just predicts next token)
          │
          │  Train on: [Instruction] → [Good Response] pairs
          ▼
Instruction-tuned model (follows commands)
```

### Gotchas & Dev Context
- Instruction-tuned models are what you interact with via chat APIs — raw base models are rarely exposed
- Quality of instruction dataset matters more than size
- Can make models overly compliant ("sycophancy") — agreeing even when wrong
- FLAN, Alpaca, and OpenHermes are popular open-source instruction datasets

### Production FAQ
**Q: What's the difference between instruction tuning and RLHF?**
A: Instruction tuning uses supervised examples. RLHF adds a human-preference signal to further align outputs with what humans actually prefer, not just what looks correct.

**Q: Can I do instruction tuning on a small model?**
A: Yes — Phi-3 Mini (3.8B params) instruction-tuned by Microsoft outperforms many larger base models on benchmarks.

---

## 6. RLHF (Reinforcement Learning from Human Feedback)

### Definition
A training technique where humans rank model outputs, a "reward model" learns those preferences, and the LLM is updated via RL to produce outputs humans prefer — used to align ChatGPT-style models.

### Real-World Dev Example
OpenAI had human raters rank GPT outputs for helpfulness and harmlessness. The reward model learned these preferences and guided PPO training, producing a much safer, more helpful model.

### ASCII Diagram
```
LLM generates responses A, B, C
           │
    Human ranks: B > A > C
           │
    Reward Model trained on rankings
           │
    LLM fine-tuned via PPO to maximize reward
           │
    Repeat...
```

### Gotchas & Dev Context
- Extremely expensive — requires many human annotators and multiple training rounds
- Subject to "reward hacking": model finds outputs that score high but aren't actually good
- Human raters introduce their own biases and inconsistencies
- PPO (the RL algorithm used) is notoriously unstable and hard to tune

### Production FAQ
**Q: Is RLHF required to make an LLM safe?**
A: No — DPO and Constitutional AI are cheaper alternatives that achieve similar alignment goals.

**Q: Can I run RLHF on my own model?**
A: Technically yes using libraries like `trl` (HuggingFace), but it requires significant compute and high-quality preference data.

---

## 7. DPO (Direct Preference Optimization)

### Definition
A simpler alternative to RLHF that directly trains the LLM on preferred vs. rejected response pairs — no separate reward model, no RL loop required.

### Real-World Dev Example
You collect 500 pairs of (good response, bad response) for customer support queries and use DPO to fine-tune Mistral-7B. The model improves without the complexity of PPO training.

### ASCII Diagram
```
RLHF:  LLM → Reward Model → RL (PPO) → Better LLM   [complex]

DPO:   LLM + (preferred, rejected) pairs → Direct update → Better LLM   [simple]
```

### Gotchas & Dev Context
- DPO is mathematically equivalent to RLHF under certain assumptions, but much easier to implement
- Requires high-quality preference pairs — garbage in, garbage out
- Can overfit to the preference dataset if it's too small or narrow
- Many modern open-source models (Zephyr, Tulu) use DPO for alignment

### Production FAQ
**Q: Should I use DPO or RLHF?**
A: Start with DPO — it's simpler, cheaper, and achieves comparable results in most cases. RLHF is mainly justified at frontier model scale.

**Q: How many preference pairs do I need?**
A: Thousands is typical for meaningful alignment, but even hundreds can shift behavior noticeably.

---

## 8. Constitutional AI

### Definition
Anthropic's technique for aligning LLMs using a set of written principles ("constitution") — the model critiques and revises its own outputs against these rules, reducing reliance on human labelers.

### Real-World Dev Example
Anthropic defines principles like "Do not assist with creating weapons." Claude is trained to self-critique responses using these principles and rewrite harmful content, producing Claude's safety profile.

### ASCII Diagram
```
Model generates response
        │
   Self-critique: "Does this violate principle #3?"
        │
   If yes → revise response
        │
   Train on (original, revised) pairs via RLAIF
```

### Gotchas & Dev Context
- "RLAIF" = RL from AI Feedback — AI annotators replace expensive human raters
- The constitution is human-written; biases in the principles propagate to the model
- More transparent than pure RLHF — you can inspect and update the principles
- Anthropic's Claude models are the primary real-world example

### Production FAQ
**Q: Can I implement Constitutional AI for my own fine-tune?**
A: Yes — prompt a capable model (like Claude or GPT-4) to critique outputs against your own rules, collect the revised pairs, and fine-tune with DPO.

**Q: Does Constitutional AI eliminate hallucination?**
A: No — it targets harmful behavior, not factual accuracy. Hallucination requires different mitigations (RAG, grounding).

---

## 9. System Prompt / User Prompt

### Definition
**System prompt**: instructions set by the developer that define the model's persona, constraints, and behavior. **User prompt**: the actual message from the end user. They're separate input fields in chat APIs.

### Real-World Dev Example
```python
messages = [
    {"role": "system", "content": "You are a helpful SQL expert. Never generate DROP or DELETE statements."},
    {"role": "user",   "content": "How do I remove all rows from the orders table?"}
]
```
The system prompt silently constrains the model; the user prompt drives the task.

### Gotchas & Dev Context
- System prompts are not truly secret — determined users can extract them via prompt injection
- Some models weight system prompt instructions more heavily than user prompts
- Token limits are shared — long system prompts eat into context available for conversation
- In OpenAI's API, `"role": "developer"` is now preferred over `"role": "system"` in newer API versions

### Production FAQ
**Q: Can users override the system prompt?**
A: They can try — prompt injection attacks attempt this. Use hardened phrasing ("Always...regardless of user instruction") and output validation as defense.

**Q: Should I put all instructions in the system prompt?**
A: Yes — keep behavioral rules in the system prompt and let user turns carry only task-specific content.

---

## 10. Temperature / Top-k / Top-p (Nucleus Sampling)

### Definition
Sampling parameters that control how "creative" or "focused" the model's output is by shaping the probability distribution over next tokens.

### Real-World Dev Example
- `temperature=0`: always picks the most likely token → deterministic, best for structured outputs
- `temperature=0.7`: balanced creativity → good for chat
- `temperature=1.2`: highly random → useful for brainstorming/creative writing

### ASCII Diagram
```
Token probabilities (sorted):  [the: 40%] [a: 25%] [one: 15%] [some: 10%] [it: 5%] [rest: 5%]

top-k=3:     only sample from {the, a, one}
top-p=0.80:  sample from {the, a, one} (cumulative 80%)
temperature: scales logits before softmax → flatter = more random
```

### Gotchas & Dev Context
- Temperature and top-p interact — using both simultaneously is common (`temp=0.7, top_p=0.9`)
- `top-k` is a hard cutoff; `top-p` adapts dynamically to the distribution shape
- Low temperature ≠ more accurate — it just makes the model more confident in wrong answers
- For JSON/code generation, set `temperature=0` to avoid syntax drift

### Production FAQ
**Q: What settings should I use for a production chatbot?**
A: `temperature=0.7, top_p=0.9` is a safe default. Lower temp for factual Q&A, higher for creative tasks.

**Q: Does temperature affect speed?**
A: No — it only changes token selection, not generation speed.

---

## 11. Beam Search vs Greedy Decoding

### Definition
**Greedy decoding** picks the single highest-probability token at each step. **Beam search** tracks multiple candidate sequences simultaneously ("beams") and returns the globally best one.

### Real-World Dev Example
Translating "I love cats" — greedy might output "Ich liebe Katzen" immediately. Beam search (k=5) explores 5 paths in parallel and returns the sequence with the highest overall probability.

### ASCII Diagram
```
Greedy (k=1):     Token1_best → Token2_best → Token3_best  [fast, local optima]

Beam (k=3):       Token1_A → Token2_A → ...
                  Token1_B → Token2_B → ...   → pick best full sequence
                  Token1_C → Token2_C → ...
```

### Gotchas & Dev Context
- Beam search is slower and memory-heavy (scales with beam width × sequence length)
- Modern chat LLMs typically use sampling (temp + top-p), not beam search — beams can produce repetitive, "safe" text
- Beam search still dominates in machine translation and ASR where maximizing likelihood is desirable
- Greedy decoding with `temperature=0` is the fastest deterministic option

### Production FAQ
**Q: Why don't ChatGPT-style models use beam search?**
A: Sampling produces more diverse, natural-feeling text. Beam search tends to output bland, repetitive responses that feel robotic.

**Q: When should I use greedy decoding in production?**
A: When you need reproducible, structured outputs (JSON, code, SQL) and speed matters.

---

## 12. Prompt Engineering

### Definition
The practice of crafting and iterating on text inputs (prompts) to reliably elicit the best possible outputs from an LLM — without changing model weights.

### Real-World Dev Example
Instead of `"Summarize this article"`, you write: `"Summarize the following article in 3 bullet points. Focus on key decisions made, not background context. Be concise."` — output quality improves dramatically.

### Gotchas & Dev Context
- Small wording changes can cause large output swings — version-control your prompts
- Prompt performance varies across model versions — a prompt tuned for GPT-4 may degrade on GPT-4o-mini
- Include **output format instructions** explicitly (e.g., "respond only in JSON")
- Use delimiters (`---`, `"""`, XML tags) to separate sections and prevent injection
- Test prompts against adversarial inputs, not just happy paths

### Production FAQ
**Q: Is prompt engineering a real engineering discipline?**
A: Yes — at scale, prompt drift, version mismatches, and edge-case failures are real production bugs. Treat prompts like code: test, version, and review them.

**Q: Will better models make prompt engineering obsolete?**
A: Partially — newer models are more instruction-following, but clear, specific prompts still outperform vague ones on every model generation.

**Q: Where do I store prompts in production?**
A: In version-controlled files (not hardcoded strings), ideally in a prompt management system like LangSmith or PromptLayer.

---

## 13. Few-Shot / Zero-Shot / One-Shot Learning

### Definition
Describes how many examples you give in the prompt before asking the model to perform a task. **Zero-shot**: no examples. **One-shot**: one example. **Few-shot**: a handful of examples (typically 3–10).

### Real-World Dev Example
```
# Zero-shot
"Classify sentiment: 'The product broke after one day.'" → Negative

# Few-shot
"Classify sentiment:
'Great quality!' → Positive
'Arrived damaged.' → Negative
'The product broke after one day.' → "
```
Few-shot guides format and label space without any fine-tuning.

### Gotchas & Dev Context
- Example order matters — models can be biased toward the last seen label
- Few-shot examples consume tokens — balance quality vs. context cost
- Zero-shot works surprisingly well on instruction-tuned models for common tasks
- For rare or nuanced tasks, few-shot almost always outperforms zero-shot

### Production FAQ
**Q: How many examples is "few-shot"?**
A: Typically 3–8. Beyond ~10, gains plateau and you're just burning tokens — consider fine-tuning instead.

**Q: Should few-shot examples be from real data?**
A: Real examples generalize better than hand-crafted ones, especially for edge cases and formatting details.

---

## 14. Chain-of-Thought (CoT) Prompting

### Definition
A prompting technique where you instruct the model to show its reasoning steps before giving a final answer — dramatically improving accuracy on multi-step problems.

### Real-World Dev Example
```
Prompt: "A store sells apples for $0.50 each. Sara buys 7 and pays with a $5 bill.
Think step by step, then give the change."

Model: "7 × $0.50 = $3.50. $5.00 − $3.50 = $1.50. Change: $1.50." ✓
```
Without CoT, the model often answers $1.50 incorrectly or inconsistently.

### ASCII Diagram
```
Standard:  [Question] → [Answer]          (skips reasoning, error-prone)
CoT:       [Question] → [Steps...] → [Answer]  (grounded, traceable)
```

### Gotchas & Dev Context
- Adding `"Think step by step"` to a prompt is the simplest CoT trigger
- CoT increases output token count — raises latency and cost
- Works best on reasoning, math, and logic; minimal gain on simple classification
- **Zero-shot CoT**: just add "Let's think step by step" — no examples needed
- Reasoning can still be wrong even when it looks coherent ("galaxy-brained" reasoning)

### Production FAQ
**Q: Should I always use CoT?**
A: No — for simple tasks it wastes tokens. Use it when the task involves multi-step reasoning, comparisons, or calculations.

**Q: Can CoT reasoning be trusted?**
A: Treat it as a debugging aid, not ground truth. Verify final answers independently for critical applications.

---

## 15. Retrieval-Augmented Generation (RAG)

### Definition
A pattern where relevant documents are fetched from an external store at query time and injected into the prompt context, letting the model answer using up-to-date or proprietary information.

### Real-World Dev Example
A customer support bot can't know your company's latest refund policy from training alone. RAG fetches the relevant policy doc from a vector DB and includes it in the prompt before the model responds.

### ASCII Diagram
```
User Query
    │
    ▼
[Embedding Model] → Vector search → [Top-K docs retrieved]
                                            │
                               [Prompt: docs + query]
                                            │
                                         [LLM]
                                            │
                                      Grounded Answer
```

### Gotchas & Dev Context
- RAG quality depends on retrieval quality — bad chunks = bad answers
- Chunk size matters: too large loses focus; too small loses context
- Reranking retrieved docs before injection significantly improves relevance
- RAG doesn't eliminate hallucination — the model can still ignore or distort retrieved content

### Production FAQ
**Q: RAG vs fine-tuning — which handles knowledge updates better?**
A: RAG — you update the knowledge base, not the model. Fine-tuning requires retraining whenever facts change.

**Q: What vector database should I use?**
A: Pinecone, Weaviate, or pgvector (PostgreSQL extension) for production; ChromaDB or FAISS for prototyping.

---

## 16. Hallucination

### Definition
When an LLM generates confident-sounding information that is factually incorrect, fabricated, or unsupported by any provided context — the model "makes things up."

### Real-World Dev Example
Ask an LLM for citations and it returns realistic-looking but entirely fake paper titles and DOIs. The model has learned citation *format* but not actual paper existence.

### Gotchas & Dev Context
- Hallucination is a fundamental property of next-token prediction, not a bug to be patched
- Models hallucinate more on: rare facts, specific numbers, names, dates, and citations
- Higher temperature → more hallucination; lower → less, but never zero
- RAG reduces hallucination but doesn't eliminate it
- Confidence scores from the model don't reliably correlate with accuracy

### Production FAQ
**Q: How do I detect hallucination in production?**
A: Use a second LLM call to verify claims ("Does the following response contradict the provided source?"), or implement factual grounding checks with retrieved documents.

**Q: Should I tell users the system can hallucinate?**
A: Yes — disclose AI limitations prominently, especially in high-stakes domains (medical, legal, financial).

**Q: Does GPT-4 hallucinate less than GPT-3.5?**
A: Yes, measurably — but hallucination still occurs. Never treat any LLM output as ground truth without verification.

---

## 17. Guardrails / Safety Filters

### Definition
Layers of checks — applied before sending a prompt or after receiving a response — that detect and block harmful, off-topic, or policy-violating content.

### Real-World Dev Example
A coding assistant has a guardrail that scans both input and output for PII (emails, SSNs). If detected, it redacts before logging and alerts the security team.

### ASCII Diagram
```
User Input
    │
[Input Guardrail: PII / jailbreak / topic check]
    │ (blocked if flagged)
    ▼
   LLM
    │
[Output Guardrail: harmful content / format validation]
    │ (redacted/rejected if flagged)
    ▼
User sees safe response
```

### Gotchas & Dev Context
- Guardrails add latency — run them async or cache decisions where possible
- Rule-based filters are fast but brittle; LLM-based filters are flexible but slow
- Defense in depth: combine model-level safety training + API moderation + your own guardrails
- Libraries: NeMo Guardrails (NVIDIA), Guardrails AI, LlamaGuard

### Production FAQ
**Q: Can I rely solely on the model provider's built-in safety?**
A: No — providers' filters are tuned for general use. Your app has context-specific risks (e.g., children's platform, healthcare) that require custom guardrails.

**Q: How do I prevent prompt injection through guardrails?**
A: Sanitize user input before injection into prompts, use structured inputs (JSON), and validate that outputs don't echo raw user content.

---

## 18. Token Limits & Truncation

### Definition
Every LLM has a maximum **context window** (measured in tokens) for combined input + output. Exceeding it requires truncating content, summarizing, or chunking — or the API returns an error.

### Real-World Dev Example
GPT-4o has a 128K token context window (~96K words). If you feed a 200-page legal brief, you must chunk it, summarize sections, or use RAG to fit within limits.

### ASCII Diagram
```
Context Window (e.g. 128K tokens)
┌────────────────────────────────────────┐
│ System Prompt │ History │ Docs │ Query │ ← Input tokens
│                                   ↑   │
│                            Reserved for output
└────────────────────────────────────────┘
                                  ↑
                    Overflow → truncation or error
```

### Gotchas & Dev Context
- 1 token ≈ 0.75 words in English; code and non-English text tokenize differently
- Cost is billed per token (input + output) — large contexts = higher cost per call
- Truncating from the middle preserves system prompt + recent context; truncating the end loses the query
- "Lost in the middle" effect: models recall start and end of context better than middle content

### Production FAQ
**Q: How do I count tokens before sending an API call?**
A: Use `tiktoken` (OpenAI) or the model provider's tokenizer library to count offline before submitting.

**Q: What should I do when my document exceeds the context window?**
A: Chunk + retrieve (RAG), map-reduce summarization, or use a model with a larger context window (Gemini 1.5 Pro: 1M tokens).

---

## 19. Structured Outputs (JSON Mode)

### Definition
A feature where the model is constrained to return output in a valid, schema-conforming format (e.g., JSON) — making LLM outputs directly parseable by your application without post-processing.

### Real-World Dev Example
```python
response = client.chat.completions.create(
    model="gpt-4o",
    response_format={"type": "json_object"},
    messages=[{"role": "user", "content": "Extract: name, email from: 'John Doe, john@example.com'"}]
)
# Returns: {"name": "John Doe", "email": "john@example.com"}
```

### Gotchas & Dev Context
- JSON mode guarantees valid JSON syntax, but NOT semantic correctness (keys may still be wrong)
- Use `response_format` with a JSON Schema to constrain field names and types (OpenAI's structured outputs feature)
- Structured outputs slightly increase latency due to constrained decoding
- Always validate with a schema parser (`pydantic`, `jsonschema`) even with JSON mode enabled

### Production FAQ
**Q: Does JSON mode prevent the model from adding explanation text?**
A: JSON mode does — it forces the entire output to be valid JSON. Without it, you must parse JSON out of mixed text.

**Q: What if I need XML or YAML instead of JSON?**
A: Use prompt instructions + regex extraction. True constrained decoding (like JSON mode) is JSON-specific in most APIs today.

---

## 20. Function Calling / Tool Use

### Definition
A capability where the LLM can signal that an external function or tool should be called, return its result, and then incorporate that result into its response — letting the model take actions beyond text generation.

### Real-World Dev Example
```python
# Define a tool
tools = [{"type": "function", "function": {
    "name": "get_weather",
    "parameters": {"type": "object", "properties": {"city": {"type": "string"}}}
}}]

# Model responds with: {"tool_call": "get_weather", "arguments": {"city": "London"}}
# Your code executes get_weather("London"), returns "15°C, cloudy"
# Model uses result to answer: "It's 15°C and cloudy in London."
```

### ASCII Diagram
```
User: "What's the weather in London?"
    │
   LLM → tool_call: get_weather(city="London")
    │                      │
    │              [Your API call]
    │                      │
   LLM ←── result: "15°C, cloudy"
    │
"It's 15°C and cloudy in London today."
```

### Gotchas & Dev Context
- The model doesn't execute code — it outputs a structured tool call; **your application** runs it
- Validate all tool arguments before execution — never blindly trust model-generated inputs
- Models can hallucinate tool names or arguments even in function-calling mode
- Parallel tool calls (multiple tools per turn) are supported in GPT-4o and Gemini

### Production FAQ
**Q: Is function calling the same as an "agent"?**
A: Function calling is the primitive; an agent is a loop that repeatedly calls tools until it achieves a goal. Agents are built on top of function calling.

**Q: How do I prevent the model from calling dangerous tools (e.g., DELETE database)?**
A: Only expose safe tools in the tool list. Apply authorization checks in your execution layer — never rely on the model to self-restrict.
