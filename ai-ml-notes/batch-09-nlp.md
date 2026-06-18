# Batch 9 — NLP & Text Processing
> How machines read, understand, and generate human language.

---

## 1. Natural Language Processing (NLP)

### Definition
NLP is the field of AI that gives computers the ability to read, understand, and generate human language — text or speech.

### Real-World Dev Example
A support ticket system that automatically reads a customer complaint like "My order hasn't arrived in 3 weeks!" and routes it to the shipping team — without a human reading it first.

### ASCII Diagram
```
Raw Text → [NLP Pipeline] → Structured Insight
             tokenize
             classify
             extract
```

### Gotchas & Dev Context
- Language is ambiguous — "bank" means different things in different sentences
- NLP models are trained on specific languages/domains; a model trained on news articles may fail on medical text
- Modern NLP is almost entirely transformer-based (BERT, GPT, etc.)
- Don't confuse NLP (understanding) with NLG (generation) — both are sub-areas

### Production FAQ
**Q: Do I need to train a custom NLP model?**
A: Rarely from scratch. Fine-tune a pre-trained model (e.g., BERT via HuggingFace) on your domain data instead.

**Q: Why does my NLP model perform well on English but poorly on regional languages?**
A: Most pre-trained models are English-heavy. Use multilingual models like `mBERT` or `XLM-R` for other languages.

---

## 2. Text Preprocessing (Tokenization, Stemming, Lemmatization)

### Definition
Text preprocessing is cleaning and transforming raw text into a format models can work with. It includes breaking text into words (tokenization), reducing words to their root (stemming/lemmatization), and removing noise.

### Real-World Dev Example
Before feeding product reviews into a sentiment model, you tokenize `"Running shoes are great!"` → `["Running", "shoes", "are", "great"]`, then lemmatize → `["run", "shoe", "be", "great"]`.

### ASCII Diagram
```
"Flies are flying fast"
       ↓ Tokenize
["Flies", "are", "flying", "fast"]
       ↓ Lemmatize
["fly",   "be",  "fly",   "fast"]

Stemming (cruder):  ["fli", "are", "fli", "fast"]
```

### Gotchas & Dev Context
- **Stemming** chops word endings (fast, crude) — `"studies"` → `"studi"` (not a real word)
- **Lemmatization** uses vocabulary + grammar rules — `"studies"` → `"study"` (correct)
- Modern transformer models (BERT, GPT) do **subword tokenization** (BPE/WordPiece) — skip classic stemming
- Use `spaCy` for production lemmatization; `NLTK` for quick experiments

### Production FAQ
**Q: Should I use stemming or lemmatization?**
A: Lemmatization for quality; stemming when speed matters. For transformer-based pipelines, neither is usually needed.

**Q: My tokenizer splits "New York" into two tokens — is that a problem?**
A: Yes for NER. Use phrase detection or named entity-aware tokenizers to keep multi-word expressions together.

---

## 3. Stop Words

### Definition
Stop words are common words (like "the", "is", "at") that carry little meaning and are usually removed before text analysis to reduce noise.

### Real-World Dev Example
Building a keyword extractor for articles — removing stop words from `"The model is very good at learning"` leaves `["model", "good", "learning"]`, which are the meaningful terms.

### Gotchas & Dev Context
- Standard lists: NLTK and spaCy both provide stop word sets per language
- **Don't blindly remove stop words for all tasks** — sentiment analysis needs "not", "no", "very"
- For search engines, removing stop words can break queries like `"to be or not to be"`
- In transformer models, stop words are usually kept — the model learns to weight them down itself

### Production FAQ
**Q: Should I remove stop words before feeding text to BERT?**
A: No. BERT handles context internally. Stop word removal is mainly for classical ML (TF-IDF + logistic regression pipelines).

**Q: What if my domain has custom stop words (e.g., "patient", "doctor" appear in every medical note)?**
A: Build a custom stop word list by checking high-frequency, low-information words in your corpus.

---

## 4. TF-IDF

### Definition
TF-IDF (Term Frequency–Inverse Document Frequency) is a numerical score that measures how important a word is in a specific document relative to a collection of documents. Frequent words across all docs get penalized.

### Real-World Dev Example
In a set of 10,000 news articles, the word "the" appears everywhere (low IDF), but "earthquake" appears only in 12 articles — so "earthquake" gets a high TF-IDF score in those articles.

### ASCII Diagram
```
TF  = (count of word in doc) / (total words in doc)
IDF = log(total docs / docs containing word)

TF-IDF = TF × IDF
```

### Gotchas & Dev Context
- TF-IDF doesn't understand meaning — `"bank"` (river) and `"bank"` (finance) get the same score
- Use `TfidfVectorizer` from `scikit-learn` — works out of the box
- Great baseline for text classification before reaching for transformers
- Sparse representation — doesn't capture word relationships

### Production FAQ
**Q: When should I use TF-IDF vs embeddings?**
A: TF-IDF is fast and interpretable — good for small datasets or as a baseline. Use embeddings when you need semantic understanding.

**Q: My TF-IDF model performs well on training data but poorly on new docs with new vocabulary.**
A: TF-IDF can't generalize to unseen words (OOV problem). Switch to embeddings or at least use character n-grams.

---

## 5. Named Entity Recognition (NER)

### Definition
NER is the task of identifying and classifying named entities in text — like people, organizations, locations, dates, and monetary values.

### Real-World Dev Example
A legal document parser reads `"Apple Inc. agreed to pay $1.2B to the EU by March 2025"` and extracts: `ORG: Apple Inc.`, `MONEY: $1.2B`, `ORG: EU`, `DATE: March 2025`.

### ASCII Diagram
```
"Elon Musk founded SpaceX in 2002 in California."
  └──PERSON──┘         └─ORG─┘  └DATE┘  └──LOC──┘
```

### Gotchas & Dev Context
- Pre-trained models (spaCy, BERT-NER) work well for common entities; fine-tune for domain-specific ones (e.g., drug names, part numbers)
- NER is sensitive to casing — `"apple"` vs `"Apple"` matters
- Nested entities (entity within entity) are hard — most models don't support them out of the box
- Use `spaCy` or HuggingFace `token-classification` pipeline for quick integration

### Production FAQ
**Q: My NER misses company names that aren't in training data.**
A: Supplement with a gazetteer (lookup list) or fine-tune on your domain corpus.

**Q: How do I evaluate NER performance?**
A: Use F1 score per entity type. Partial matches (e.g., "New" vs "New York") can skew metrics — use exact vs. partial match modes carefully.

---

## 6. Part-of-Speech Tagging

### Definition
POS tagging labels each word in a sentence with its grammatical role — noun, verb, adjective, adverb, etc.

### Real-World Dev Example
A grammar checker tags `"She runs fast"` → `[She/PRON, runs/VERB, fast/ADV]` and catches `"She run fast"` as grammatically incorrect.

### ASCII Diagram
```
Sentence:  "The quick brown fox jumps"
POS Tags:   DET  ADJ   ADJ   NOUN  VERB
```

### Gotchas & Dev Context
- Same word, different POS: `"I can can a can"` — all three "can"s have different tags
- POS is context-dependent; most modern taggers use neural models (98%+ accuracy on standard English)
- `spaCy`'s `.pos_` and `.tag_` give coarse vs. fine-grained tags
- POS tagging feeds into higher-level tasks: parsing, NER, and dependency analysis

### Production FAQ
**Q: Do I need POS tagging if I'm using BERT?**
A: Usually not explicitly — BERT encodes grammar implicitly. POS is useful when you need interpretable linguistic features or rule-based pipelines.

**Q: POS accuracy drops on my domain text (e.g., social media). Why?**
A: Training data mismatch. Social media text (abbreviations, emojis, slang) differs from standard corpora. Fine-tune or use a model trained on tweets.

---

## 7. Sentiment Analysis

### Definition
Sentiment Analysis classifies the emotional tone of a piece of text — typically as positive, negative, or neutral (or on a numeric scale).

### Real-World Dev Example
An e-commerce platform processes 50,000 product reviews nightly and flags products with a sentiment score drop > 10% week-over-week for quality team review.

### ASCII Diagram
```
"Absolutely love this product!" → [Sentiment Model] → POSITIVE (0.97)
"Worst purchase ever."          → [Sentiment Model] → NEGATIVE (0.03)
```

### Gotchas & Dev Context
- Negation is tricky — `"not bad"` is positive; naive models may call it negative
- Sarcasm is very hard — `"Oh great, another bug"` is negative despite positive words
- Domain matters: `"the movie was sick"` → positive (slang), but medical NLP would tag "sick" negatively
- Pre-trained models: `cardiffnlp/twitter-roberta-base-sentiment` (HuggingFace) works well out of the box

### Production FAQ
**Q: My sentiment model gives wrong results on industry-specific text.**
A: Fine-tune on labeled domain data (even 1,000–2,000 examples helps significantly).

**Q: Should I use 3-class (pos/neg/neutral) or 5-star rating prediction?**
A: 3-class is simpler and more robust. Use 5-star only if you have granular labeled training data to match.

---

## 8. Text Classification

### Definition
Text Classification assigns a predefined category to a piece of text — like spam detection, topic labeling, or intent recognition.

### Real-World Dev Example
A helpdesk system reads incoming emails and routes them: `"Reset my password"` → `category: account_access`, `"Invoice not received"` → `category: billing`.

### ASCII Diagram
```
Input Text → [Encoder] → [Classifier Head] → Label
             (BERT)      (linear layer)
```

### Gotchas & Dev Context
- For few classes with lots of labeled data → fine-tune a transformer
- For many classes with little data → try zero-shot classification (`facebook/bart-large-mnli`)
- Class imbalance is common (e.g., 95% non-spam) — use weighted loss or oversample minority class
- Always check a confusion matrix, not just accuracy

### Production FAQ
**Q: My classifier has high accuracy but terrible recall on the minority class.**
A: Accuracy is misleading for imbalanced datasets. Optimize for F1 or use `class_weight='balanced'` in sklearn.

**Q: How many training examples do I need per class?**
A: Fine-tuning BERT can work with as few as 100–500 examples per class. Below that, try few-shot or zero-shot approaches.

---

## 9. Text Summarization (Extractive vs Abstractive)

### Definition
Text Summarization automatically produces a shorter version of a document.
- **Extractive**: picks actual sentences from the original text.
- **Abstractive**: generates new sentences that capture the meaning (like a human would).

### Real-World Dev Example
A legal-tech app summarizes 50-page contracts: extractive pulls the 5 most important clauses verbatim; abstractive generates a plain-English paragraph explaining what you're agreeing to.

### ASCII Diagram
```
EXTRACTIVE:
[Doc] → score sentences → pick top-N → [Summary]

ABSTRACTIVE:
[Doc] → [Encoder-Decoder Model] → generate new text → [Summary]
```

### Gotchas & Dev Context
- Abstractive summaries can **hallucinate** facts not in the source — verify for high-stakes use cases
- Extractive is safer but less fluent; abstractive is more readable but riskier
- Use `facebook/bart-large-cnn` or `google/pegasus-xsum` for abstractive summarization
- Long documents (>512 tokens) need chunking or models with extended context (Longformer, GPT-4)

### Production FAQ
**Q: Which approach is better for legal/medical documents?**
A: Extractive — hallucination risk is unacceptable. Only use abstractive with human review.

**Q: How do I evaluate summarization quality?**
A: Use **ROUGE scores** (overlap with reference summaries). ROUGE-L is most commonly cited, but also do human eval for fluency.

---

## 10. Machine Translation

### Definition
Machine Translation (MT) automatically converts text from one language to another while preserving meaning.

### Real-World Dev Example
A global SaaS app uses the Helsinki-NLP translation model to automatically translate user-submitted bug reports from Spanish and French into English before routing them to the engineering queue.

### ASCII Diagram
```
"Bonjour le monde"
        ↓
[Encoder] → context vectors → [Decoder]
        ↓
"Hello world"
```

### Gotchas & Dev Context
- Quality degrades on: rare languages, domain-specific jargon, and idioms
- Use `Helsinki-NLP/opus-mt-*` models on HuggingFace for open-source MT
- Google Translate / DeepL APIs are production-grade and cheap for moderate volume
- Always post-edit MT output for customer-facing content in critical domains

### Production FAQ
**Q: Should I build my own MT model or use an API?**
A: Use APIs (DeepL/Google) unless you have privacy constraints or a highly specialized domain requiring fine-tuning.

**Q: How do I measure translation quality automatically?**
A: Use **BLEU score** (measures n-gram overlap with reference translations). COMET is more modern and correlates better with human judgments.

---

## 11. Question Answering

### Definition
Question Answering (QA) is an NLP task where a model reads a context passage and returns the exact answer to a question — without you searching manually.

### Real-World Dev Example
An internal HR chatbot is given the company policy PDF. An employee asks "How many sick days do I get per year?" — the QA model finds and returns "Employees receive 12 sick days per year" from the document.

### ASCII Diagram
```
Context: "Employees receive 12 sick days per year..."
Question: "How many sick days?"
                ↓
        [QA Model (BERT)]
                ↓
Answer: "12 sick days"  [span extracted from context]
```

### Gotchas & Dev Context
- **Extractive QA**: returns a span from the context (BERT-based) — no hallucination risk
- **Generative QA**: generates a free-form answer (GPT-based) — may hallucinate
- Model fails if the answer isn't in the context — add a "no answer" confidence threshold
- Use `deepset/roberta-base-squad2` for extractive QA out of the box

### Production FAQ
**Q: What's the difference between QA and RAG?**
A: QA answers from a fixed context. RAG first *retrieves* relevant chunks from a large corpus, then passes them as context to a QA/generative model.

**Q: My QA model returns wrong spans. How do I improve it?**
A: Fine-tune on domain-specific QA pairs (SQuAD format). Even 500–1,000 labeled examples help significantly.

---

## 12. Semantic Search / Vector Search

### Definition
Semantic Search finds documents or passages that are *meaningfully similar* to a query — not just keyword matches. It works by comparing embedding vectors in high-dimensional space.

### Real-World Dev Example
A user searches `"tips for sleeping better"` — keyword search misses articles titled `"Improving sleep quality"`, but vector search finds them because their embeddings are close.

### ASCII Diagram
```
Query: "sleeping better"  → [Embed] → [0.12, 0.85, ...]
Doc A: "improve sleep"    → [Embed] → [0.11, 0.83, ...]  ← HIGH similarity
Doc B: "stock market tips"→ [Embed] → [0.71, 0.02, ...]  ← LOW similarity
```

### Gotchas & Dev Context
- Requires an **embedding model** (e.g., `sentence-transformers/all-MiniLM-L6-v2`) and a **vector database** (Pinecone, Weaviate, pgvector, Chroma)
- Cosine similarity is the standard distance metric for text embeddings
- Exact keyword match often complements vector search — use **hybrid search** for best results
- Index size grows fast — monitor memory usage in production

### Production FAQ
**Q: Which vector DB should I use?**
A: Chroma for local/dev, Pinecone for managed cloud, pgvector if you're already on PostgreSQL.

**Q: My semantic search returns irrelevant results for short queries.**
A: Short queries have weak signals. Try query expansion (add synonyms) or use a reranker model (e.g., `cross-encoder/ms-marco-MiniLM`) as a second pass.

---

## 13. Text-to-Speech (TTS) / Speech-to-Text (STT)

### Definition
- **TTS**: converts written text into spoken audio.
- **STT** (also called ASR — Automatic Speech Recognition): converts spoken audio into written text.

### Real-World Dev Example
A banking IVR system uses STT to transcribe a caller saying `"Check my balance"`, routes it to intent detection, then uses TTS to speak back: `"Your balance is $1,240."` — no human agent needed.

### ASCII Diagram
```
STT:  [Audio] → [ASR Model] → "Check my balance"
TTS:  "Your balance is $1,240" → [TTS Model] → [Audio]
```

### Gotchas & Dev Context
- STT quality degrades with: background noise, accents, domain jargon
- TTS quality varies wildly — neural TTS (ElevenLabs, Azure Neural Voice) sounds natural; older systems sound robotic
- Latency matters: real-time STT requires streaming models (not batch)
- Whisper (OpenAI) is the go-to open-source STT; Coqui TTS for open-source TTS

### Production FAQ
**Q: Which STT API is most accurate in production?**
A: Google Cloud Speech-to-Text and AWS Transcribe are strong managed options. For self-hosted, Whisper large-v3 is state-of-the-art.

**Q: How do I handle domain-specific words (e.g., drug names, product SKUs) in STT?**
A: Use custom vocabulary / phrase hints features provided by cloud STT APIs, or fine-tune Whisper on domain audio.

---

## 14. Whisper (OpenAI)

### Definition
Whisper is an open-source speech recognition model by OpenAI, trained on 680,000 hours of multilingual audio. It transcribes speech to text with high accuracy across 99+ languages.

### Real-World Dev Example
A podcast platform runs Whisper on each new episode upload to generate searchable transcripts and auto-captions — cutting manual transcription costs to near zero.

### ASCII Diagram
```
audio.mp3 → [Whisper Model] → transcript.txt
             (tiny/base/      + timestamps
              small/medium/   + language detection
              large-v3)
```

### Gotchas & Dev Context
- 5 model sizes: `tiny` (fast, less accurate) → `large-v3` (slow, best accuracy)
- Runs on CPU but large models need a GPU for real-time use
- Timestamps can be word-level with `whisper-timestamped` or `stable-ts`
- Not designed for real-time streaming — use `faster-whisper` + chunking for near-real-time
- Hallucination on silent audio segments (model "invents" text) — always silence-strip inputs

### Production FAQ
**Q: Which Whisper model should I deploy?**
A: `medium` is the sweet spot for most production use. `large-v3` for maximum accuracy (requires ~10GB VRAM).

**Q: Can Whisper handle mixed-language audio?**
A: It detects language per segment but struggles with mid-sentence code-switching. Results vary; test on your actual audio.

---

## 15. Chatbot / Conversational AI

### Definition
A Chatbot is a system that conducts text (or voice) conversations with users. Modern Conversational AI uses LLMs to handle open-ended dialogue with context across multiple turns.

### Real-World Dev Example
A SaaS company deploys a GPT-4-based support chatbot. When a user says `"I can't log in"` then `"It says my account is locked"`, the bot tracks the full conversation thread and suggests the right unlock steps — not starting over each message.

### ASCII Diagram
```
Turn 1: User: "I can't log in"
Turn 2: User: "Says account locked"
        ↓
[System Prompt + Turn 1 + Turn 2] → [LLM] → "Click Forgot Password..."
        ↑
   Context Window
```

### Gotchas & Dev Context
- Multi-turn context is sent on every request — token costs accumulate fast
- Implement **conversation summarization** for long sessions to stay within context limits
- Hallucination is a real risk — ground answers with RAG for factual domains
- Use guardrails (e.g., LlamaGuard, Azure Content Safety) to prevent off-topic or harmful outputs

### Production FAQ
**Q: Rule-based chatbot vs. LLM chatbot — when to use which?**
A: Rule-based for narrow, predictable flows (e.g., appointment booking). LLM for open-ended, natural conversation with varied phrasing.

**Q: How do I prevent my chatbot from going off-topic?**
A: Use a strong system prompt, implement topic classifiers as a guard layer, and restrict the retrieval context with RAG.

---

## 16. Document Parsing / Chunking for RAG

### Definition
Document Parsing extracts clean text from raw files (PDFs, DOCX, HTML). Chunking splits that text into smaller, meaningful segments so they can be embedded and retrieved individually in a RAG pipeline.

### Real-World Dev Example
A law firm uploads 200-page contracts. The system parses each PDF, chunks them into 512-token overlapping segments, embeds each chunk, and stores them in a vector DB — so a QA bot can retrieve exactly the right clause when asked.

### ASCII Diagram
```
PDF → [Parser] → raw text
              → [Chunker] → chunk_1 (tokens 0–512)
                           chunk_2 (tokens 256–768)  ← overlap
                           chunk_3 (tokens 512–1024)
                                ↓
                         [Embed + Store in VectorDB]
```

### Gotchas & Dev Context
- **Chunk size matters**: too small = missing context; too large = dilutes retrieval precision. 256–512 tokens is a common sweet spot
- **Overlap** (e.g., 50–100 tokens) prevents splitting answers across chunk boundaries
- PDF parsing is messy — tables, multi-column layouts, and scanned PDFs need OCR (`pytesseract`, `unstructured`)
- Use `LangChain`'s `RecursiveCharacterTextSplitter` or `llama-index` for battle-tested chunking strategies
- Metadata (page number, document title) attached to each chunk is critical for citations

### Production FAQ
**Q: My RAG bot gives answers from the wrong part of the document. What's wrong?**
A: Likely a chunking or embedding issue. Check that chunks don't split mid-sentence, and that your embedding model matches the one used at query time.

**Q: How do I handle tables and figures in PDFs?**
A: Tables need special handling — use `camelot` or `pdfplumber` for structured table extraction. Figures require multimodal models (e.g., GPT-4 Vision) to interpret.
