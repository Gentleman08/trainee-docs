# Batch 10 — RAG & Vector Databases
> How to give LLMs a long-term memory using your own documents and data.

---

## 1. RAG Architecture

### Definition
RAG (Retrieval-Augmented Generation) is a pattern where an LLM is given relevant documents at query time instead of relying solely on its training data — combining a retrieval system with a generator.

### Real-World Dev Example
A company's internal helpdesk bot answers questions about HR policies by fetching the relevant policy PDF chunks first, then passing them to GPT-4 as context.

### ASCII Diagram
```
User Query
    │
    ▼
[Embedding Model] ──► Query Vector
                            │
                            ▼
                   [Vector Database] ──► Top-K Chunks
                                              │
                            ┌─────────────────┘
                            ▼
                   [LLM Prompt = Query + Chunks]
                            │
                            ▼
                       Final Answer
```

### Gotchas & Dev Context
- RAG does NOT update model weights — it's retrieval at inference time
- Quality of retrieval directly caps answer quality: garbage in, garbage out
- Latency = embedding query + vector search + LLM call (3 hops)
- Not suitable for tasks needing reasoning across ALL documents simultaneously

### Production FAQ
**Q: When does RAG fail?**
A: When the retrieval step returns irrelevant chunks. The LLM then hallucinates or says "I don't know."

**Q: RAG vs. fine-tuning — when to use which?**
A: RAG for dynamic/private knowledge that changes often. Fine-tuning for consistent style/behavior or domain-specific language patterns.

**Q: How many chunks should I retrieve?**
A: Typically 3–10 (Top-K). Too few = missing info; too many = context window bloat and noise.

---

## 2. Document Loading & Parsing

### Definition
The step of ingesting raw files (PDFs, Word docs, HTML, CSVs) and converting them into plain text that can be chunked and embedded.

### Real-World Dev Example
You load a 200-page product manual PDF, strip headers/footers, and extract clean paragraph text before feeding it into your chunking pipeline.

### Gotchas & Dev Context
- PDFs are notoriously messy — scanned PDFs need OCR (e.g., Tesseract, AWS Textract)
- Tables in PDFs often parse as garbage text; use specialized parsers (Camelot, pdfplumber)
- HTML pages need boilerplate stripping (nav bars, footers) — use `trafilatura` or `BeautifulSoup`
- Preserve metadata (source URL, page number, author) during loading — you'll need it for filtering and citations later
- Common loaders: LangChain's `PyPDFLoader`, `UnstructuredFileLoader`, `WebBaseLoader`

```python
from langchain_community.document_loaders import PyPDFLoader
docs = PyPDFLoader("manual.pdf").load()
# docs[i].metadata has {'source': 'manual.pdf', 'page': 0}
```

### Production FAQ
**Q: What's the best PDF parser?**
A: `pdfplumber` for text-heavy PDFs, `Unstructured` for mixed layouts, AWS Textract for scanned/image PDFs.

**Q: How do I handle multi-format corpora?**
A: Use LangChain's `DirectoryLoader` with format-specific sub-loaders, or the `Unstructured` library which handles 25+ formats uniformly.

---

## 3. Text Chunking Strategies

### Definition
Splitting documents into smaller pieces (chunks) so they fit within embedding model limits and retrieval returns precise, relevant segments rather than entire documents.

### Real-World Dev Example
A legal contract (50 pages) is split into ~300-token chunks so the retriever can return the exact clause about liability rather than the whole document.

### ASCII Diagram
```
Fixed (by token count):
│── 512 ──│── 512 ──│── 512 ──│

Recursive (by structure):
│ Section 1 │ Section 2 │ Sub-2.1 │ Sub-2.2 │

Semantic (by meaning shift):
│ Topic A ────────│ Topic B ──│ Topic C ───────│
```

### Gotchas & Dev Context
- **Fixed chunking**: Simple but splits mid-sentence; use overlap (e.g., 50 tokens) to prevent context loss
- **Recursive chunking**: Splits on `\n\n`, then `\n`, then `. ` — respects structure; default choice for most use cases
- **Semantic chunking**: Groups sentences by embedding similarity; best quality but slowest and costliest
- Chunk size sweet spot: 256–512 tokens for factual QA, 512–1024 for summarization tasks
- Overlap of 10–15% reduces boundary-cut information loss

### Production FAQ
**Q: What chunk size should I start with?**
A: 512 tokens with 50-token overlap is a safe default. Benchmark against your specific retrieval task.

**Q: Does chunking strategy affect accuracy that much?**
A: Yes — poor chunking is one of the top causes of RAG failure. Semantic chunking can improve retrieval recall by 10–25% on complex documents.

---

## 4. Embedding Models

### Definition
Models that convert text into dense numerical vectors (embeddings) that capture semantic meaning — similar text produces similar vectors.

### Real-World Dev Example
"How do I reset my password?" and "Steps to change login credentials" produce vectors that are very close together, so the same FAQ chunk is retrieved for both queries.

### Gotchas & Dev Context
- **OpenAI `text-embedding-ada-002`**: 1536-dim, easy to use, good general performance, costs $0.0001/1K tokens
- **OpenAI `text-embedding-3-small/large`**: Newer, cheaper, better — prefer over ada-002 for new projects
- **BGE (BAAI)**: Open-source, top leaderboard performer, free, good for on-prem deployments
- **E5 (Microsoft)**: Strong cross-lingual support, good for multilingual corpora
- **Cohere Embed v3**: Distinguishes between search queries and documents (`input_type` param) — improves retrieval precision
- All models have a **max token limit** (ada-002: 8191 tokens) — chunks exceeding this are silently truncated

```python
from openai import OpenAI
vec = OpenAI().embeddings.create(
    input="reset my password",
    model="text-embedding-3-small"
).data[0].embedding  # list of 1536 floats
```

### Production FAQ
**Q: Can I mix embedding models in one vector DB?**
A: No — all vectors must come from the same model. Switching models requires re-embedding the entire corpus.

**Q: Should I embed queries the same way as documents?**
A: Yes (same model), but Cohere's `input_type="search_query"` vs `"search_document"` distinction boosts accuracy significantly.

---

## 5. Vector Database

### Definition
A database optimized to store, index, and search high-dimensional vectors efficiently — the storage backbone of any RAG system.

### Real-World Dev Example
Your 1M product descriptions are embedded and stored in Pinecone. At query time, a user's search vector finds the 10 most similar product descriptions in milliseconds.

### Gotchas & Dev Context
| DB | Best For | Hosting |
|---|---|---|
| **Pinecone** | Managed, zero-ops, fast | Cloud only |
| **Weaviate** | Hybrid search built-in, GraphQL | Cloud + self-host |
| **Qdrant** | High performance, Rust-based, filtering | Cloud + self-host |
| **Chroma** | Local dev, prototyping, easy setup | Local |
| **Milvus** | Billion-scale, enterprise | Self-host |
| **pgvector** | Already using PostgreSQL | Self-host |

- Chroma is perfect for POCs — don't use in production at scale
- pgvector is underrated: adds vector search to your existing Postgres with no new infra
- Always store metadata alongside vectors (source, date, chunk_id) for filtering

### Production FAQ
**Q: Which vector DB should I start with?**
A: Chroma for local dev, Qdrant or Pinecone for production. pgvector if you're already on Postgres.

**Q: Do I need a vector DB if I have < 10K documents?**
A: Not necessarily — FAISS in-memory or even numpy cosine similarity can work at that scale.

---

## 6. Similarity Search

### Definition
The method used to find vectors (chunks) in the database that are most similar to the query vector — the core of retrieval.

### Real-World Dev Example
A user asks "What's the refund policy?" — the query vector is compared to all stored chunk vectors, and the top 5 most similar chunks are returned.

### ASCII Diagram
```
Query Vector Q: [0.2, 0.8, 0.5]

Cosine:    angle between Q and each vector (direction only)
Euclidean: straight-line distance between Q and each vector
Dot Product: Q · V = |Q||V|cos(θ)  (magnitude + direction)
```

### Gotchas & Dev Context
- **Cosine similarity**: Best for text (magnitude doesn't matter, only direction). Range: [-1, 1]
- **Euclidean distance**: Sensitive to vector magnitude — use only if embeddings are L2-normalized
- **Dot product**: Fastest to compute; equivalent to cosine if vectors are unit-normalized. Used internally by many ANN indexes
- Most embedding models produce **unit-normalized** vectors by default → cosine ≈ dot product
- Your vector DB's distance metric must match what the embedding model was trained with

### Production FAQ
**Q: Which metric should I default to?**
A: Cosine similarity for text embeddings — it's the standard and works reliably across all major embedding models.

**Q: Why is my similarity score always high but results are irrelevant?**
A: High cosine similarity doesn't guarantee semantic relevance — it means the vectors point in the same direction. Re-rank results with a cross-encoder to reorder by true relevance.

---

## 7. HNSW Index

### Definition
HNSW (Hierarchical Navigable Small World) is a graph-based Approximate Nearest Neighbor (ANN) index that makes vector search fast at scale by navigating a layered graph instead of scanning all vectors.

### Real-World Dev Example
Without HNSW, searching 10M vectors takes seconds. With HNSW, the same search takes milliseconds by following graph shortcuts to the nearest neighbors.

### ASCII Diagram
```
Layer 2 (sparse):  A ─────────────── E
Layer 1 (medium):  A ─── B ─── D ─── E
Layer 0 (dense):   A─B─C─D─E─F─G─H─I─J

Query enters at top layer → navigates down → finds neighbors
```

### Gotchas & Dev Context
- **ANN** = Approximate Nearest Neighbor — may miss the absolute best match, but is 100–1000× faster than exact search
- Key params: `ef_construction` (build quality, higher = slower build but better index), `M` (graph connections per node)
- Higher `ef` at search time = more accurate but slower — tune based on your latency budget
- HNSW uses significant RAM — all vectors must fit in memory
- Used by: Qdrant, Weaviate, Milvus, FAISS, pgvector

### Production FAQ
**Q: How much accuracy do I lose with ANN vs. exact search?**
A: Typically < 1–2% recall loss at 10× speedup. For RAG use cases, this is almost always acceptable.

**Q: When would I NOT use HNSW?**
A: Below ~50K vectors, brute-force exact search is fast enough and simpler. HNSW shines at 100K+ vectors.

---

## 8. Hybrid Search

### Definition
Combining vector (semantic) search with keyword (BM25/TF-IDF) search, then merging results — getting the best of both worlds.

### Real-World Dev Example
A user searches "CVE-2024-1234 vulnerability details" — keyword search nails the exact CVE number while vector search finds semantically related security advisories. Hybrid search returns both.

### ASCII Diagram
```
Query
  │
  ├──► [BM25 / Keyword Search] ──► Keyword Results
  │
  └──► [Vector Search]         ──► Semantic Results
                │                         │
                └──────────┬──────────────┘
                           ▼
                  [RRF / Score Fusion]
                           │
                           ▼
                    Final Ranked Results
```

### Gotchas & Dev Context
- **RRF (Reciprocal Rank Fusion)**: Standard score-merging formula — robust, parameter-free, preferred over weighted averaging
- Pure vector search misses exact matches (product codes, names, IDs)
- Pure keyword search misses synonyms and paraphrases
- Weaviate has hybrid search built-in; for Pinecone, you need a separate keyword index (e.g., Elasticsearch)
- α parameter controls vector vs. keyword weight (α=1 = pure vector, α=0 = pure keyword)

### Production FAQ
**Q: Should I always use hybrid search?**
A: Use it when your queries contain proper nouns, codes, or IDs that must match exactly. Pure semantic search is fine for conversational queries.

**Q: What's RRF?**
A: `RRF(d) = Σ 1/(k + rank(d))` — rewards documents that rank high in multiple result lists, regardless of score magnitude.

---

## 9. Re-Ranking

### Definition
A second-pass scoring step that reorders the initial retrieved chunks using a more powerful (but slower) relevance model — improving precision before sending to the LLM.

### Real-World Dev Example
Vector search returns 20 candidate chunks. A cross-encoder scores each (query, chunk) pair individually and reorders them — the top 5 now sent to GPT-4 are genuinely the most relevant.

### ASCII Diagram
```
[Vector DB] ──► 20 candidates (fast, approximate)
                      │
                      ▼
              [Cross-Encoder / Reranker]
              scores each (query, chunk) pair
                      │
                      ▼
              Top 5 re-ranked results ──► LLM
```

### Gotchas & Dev Context
- **Cross-encoder**: Takes (query + chunk) as one input, outputs a relevance score — more accurate than bi-encoders but O(n) calls
- **Cohere Rerank**: Managed API reranker, 1 API call for up to 1000 candidates — easiest production option
- **BGE Reranker**, **ms-marco-MiniLM**: Open-source alternatives, run locally
- Re-ranking adds ~200–500ms latency — retrieve more (Top-20), rerank, send fewer (Top-5)
- Critical for long-tail queries where vector similarity doesn't correlate with true relevance

### Production FAQ
**Q: Is re-ranking always worth the latency cost?**
A: For customer-facing QA, yes. For internal tools with simple queries, vector search alone may suffice.

**Q: Cross-encoder vs. Cohere Rerank — which to choose?**
A: Cohere Rerank for zero-infra, fast iteration. Self-hosted cross-encoder for data privacy or cost at high volume.

---

## 10. Metadata Filtering

### Definition
Pre-filtering the vector database by structured attributes (date, author, category, file type) before or alongside vector similarity search — ensuring retrieved chunks are from the right scope.

### Real-World Dev Example
A user in the Finance team queries "What's our vacation policy?" — metadata filter `department=finance` ensures only finance-specific policy chunks are retrieved, not HR docs from Engineering.

### Gotchas & Dev Context
- Filters run **before** or **alongside** ANN search (pre-filter vs. post-filter)
- Pre-filtering reduces the search space → faster but may exclude valid results
- Post-filtering applies filter after ANN → may return fewer than Top-K if many results are filtered out
- Common metadata fields: `source`, `doc_type`, `date`, `language`, `author`, `chunk_id`, `page_number`
- All vector DBs support metadata filtering; syntax varies:

```python
# Qdrant example
results = client.search(
    collection_name="docs",
    query_vector=query_vec,
    query_filter=Filter(must=[FieldCondition(key="dept", match=MatchValue(value="finance"))]),
    limit=5
)
```

### Production FAQ
**Q: Can I filter by date range?**
A: Yes — most vector DBs support range filters on numeric/timestamp metadata fields.

**Q: Does metadata filtering hurt recall?**
A: Yes, by design — it trades recall for precision and access control. Always validate that your filter logic doesn't over-restrict results.

---

## 11. Contextual Retrieval

### Definition
Anthropic's technique of prepending a chunk-specific context summary (generated by an LLM) to each chunk before embedding — dramatically improving retrieval accuracy for chunks that lack standalone context.

### Real-World Dev Example
A chunk reads: *"The net increase was $2.3M compared to the previous quarter."* Without context, this is meaningless. Contextual retrieval prepends: *"From ACME Corp Q3 2024 earnings report, revenue section:"* — now it embeds and retrieves correctly.

### ASCII Diagram
```
Original chunk:  "The net increase was $2.3M..."
                          +
LLM-generated context: "From ACME Q3 2024 earnings, revenue section"
                          │
                          ▼
         Combined text ──► Embedding ──► Vector DB
```

### Gotchas & Dev Context
- Context is prepended to the chunk at **embedding time**, not at retrieval time
- Requires an LLM call per chunk during indexing — expensive for large corpora (cache contexts aggressively)
- Anthropic reported 49% reduction in retrieval failures with this technique
- Works best for chunks that are narrative continuations (e.g., financial reports, legal docs)
- Often combined with BM25 for hybrid contextual retrieval

### Production FAQ
**Q: How long should the prepended context be?**
A: 1–3 sentences is sufficient. Longer context dilutes the chunk's own semantic signal.

**Q: Is this the same as chunk metadata?**
A: No — metadata is structured fields for filtering. Contextual retrieval is unstructured natural language prepended to the chunk text itself, affecting the embedding.

---

## 12. Parent-Child Chunking

### Definition
A strategy where documents are split into small child chunks (for precise retrieval) but the parent chunk (larger surrounding context) is what gets sent to the LLM — giving precise retrieval with rich context.

### Real-World Dev Example
A 2000-token section is split into 4 child chunks of 500 tokens each. The retriever finds the most relevant child, but the LLM receives the full 2000-token parent — ensuring it has full context to answer accurately.

### ASCII Diagram
```
Parent Chunk (2000 tokens)
├── Child 1 (500 tokens) ◄── retrieved (most similar)
├── Child 2 (500 tokens)
├── Child 3 (500 tokens)
└── Child 4 (500 tokens)

Send to LLM: Parent Chunk (full context)
```

### Gotchas & Dev Context
- Child chunks are embedded; parent chunks are stored separately (e.g., in a doc store)
- Requires maintaining a child→parent mapping (by `parent_id` metadata)
- LangChain's `ParentDocumentRetriever` implements this out of the box
- Avoids the trade-off between "small chunks for retrieval" vs. "large chunks for context"
- Can be extended to 3 levels: sentence → paragraph → section

### Production FAQ
**Q: What's the recommended child/parent size ratio?**
A: Common setup: 128–256 token children, 512–1024 token parents.

**Q: Does this increase storage costs?**
A: Slightly — you store both child embeddings and parent text. The retrieval quality gain usually justifies it.

---

## 13. Multi-Vector Retrieval

### Definition
Representing a single document or chunk with multiple vectors — e.g., embedding a summary AND individual sentences — so different query types can find the same document via different access paths.

### Real-World Dev Example
A research paper is indexed with: (1) a summary embedding, (2) each section's embedding, and (3) a hypothetical question embedding ("What does this paper answer?"). Queries match via whichever vector is most similar.

### Gotchas & Dev Context
- **HyDE (Hypothetical Document Embeddings)**: Generate a fake ideal answer to the query, embed it, use it as the search vector — often outperforms embedding the raw question
- **Summary + chunks**: Store summary vector for broad queries, child chunk vectors for specific lookups
- ColBERT-style **late interaction**: Stores one vector per token, allows fine-grained matching — very accurate but storage-heavy
- LlamaIndex's `MultiVectorIndex` supports this natively
- Increases index size proportionally to vectors-per-document

```
Document ──► [Summary]       ──► vector_1
         ──► [Section 1]     ──► vector_2
         ──► [Section 2]     ──► vector_3
         ──► [Hyp. Question] ──► vector_4
```

### Production FAQ
**Q: When is multi-vector retrieval worth the complexity?**
A: When single-vector retrieval has measurably poor recall on diverse query types — especially for long, multi-topic documents.

**Q: What is HyDE and does it work?**
A: HyDE generates a hypothetical answer to the query and embeds that instead of the raw question. It often improves recall for vague or short queries by 10–20%.

---

## 14. Knowledge Graphs + RAG

### Definition
Augmenting RAG with a structured knowledge graph (KG) — a network of entities and relationships — to handle multi-hop reasoning and precise factual lookups that pure vector search can't do.

### Real-World Dev Example
"Who is the CEO of the company that acquired Slack?" — a KG can traverse: Slack → acquired_by → Salesforce → CEO → Marc Benioff. A vector search alone would struggle with this 2-hop reasoning.

### ASCII Diagram
```
[Vector Search] ──► relevant chunks (semantic)
       +
[Knowledge Graph] ──► entity relationships (structural)
       │
       └──► Combined context ──► LLM ──► Answer
```

### Gotchas & Dev Context
- KGs excel at: entity disambiguation, relationship traversal, multi-hop Q&A
- Building a KG is expensive — requires NER + entity linking + relation extraction
- GraphRAG (Microsoft) auto-builds a KG from documents using an LLM
- Neo4j is the most common KG store for RAG integrations
- Pure GraphRAG is slower (graph traversal) — use it alongside vector RAG, not instead of it
- Best for: legal/compliance docs, org charts, product catalogs with clear entity relationships

### Production FAQ
**Q: Is GraphRAG better than standard RAG?**
A: For multi-hop factual queries, yes. For simple Q&A, standard RAG is cheaper and faster.

**Q: How hard is it to build a KG from scratch?**
A: Hard — use Microsoft's `graphrag` library or LlamaIndex's `KnowledgeGraphIndex` to automate extraction, but expect significant compute cost.

---

## 15. RAG Evaluation

### Definition
Measuring how well your RAG system retrieves relevant context and generates faithful, accurate answers — using structured metrics rather than vibes.

### Real-World Dev Example
After building a support chatbot, you run RAGAS on 100 test questions to get faithfulness=0.87, answer relevance=0.91, context recall=0.73 — identifying that context recall is the weak link (retrieval problem, not generation).

### Gotchas & Dev Context
| Metric | What It Measures | Failure Mode |
|---|---|---|
| **Faithfulness** | Is the answer grounded in retrieved context? | Hallucination |
| **Answer Relevance** | Does the answer address the question? | Off-topic responses |
| **Context Recall** | Did retrieval fetch all necessary info? | Missing chunks |
| **Context Precision** | Are retrieved chunks actually relevant? | Noisy retrieval |

- **RAGAS** is the de facto framework for RAG evaluation (uses LLM-as-judge)
- **TruLens** is another popular option with a dashboard UI
- Low faithfulness → fix the LLM prompt or add grounding instructions
- Low context recall → fix chunking, embedding, or retrieval Top-K
- Always evaluate on a **held-out test set** — never the same docs you tuned on

### Production FAQ
**Q: Do I need ground truth answers for evaluation?**
A: RAGAS can work without ground truth (using LLM-as-judge), but having a golden dataset gives you much more reliable metrics.

**Q: How often should I re-evaluate in production?**
A: After any change to chunking, embedding model, retrieval params, or prompt. Set up automated eval in your CI/CD pipeline.

---

## 16. LangChain / LlamaIndex / Haystack

### Definition
Orchestration frameworks that wire together the components of a RAG pipeline (loaders, chunkers, embedders, vector stores, LLMs) so you don't have to build each integration from scratch.

### Real-World Dev Example
With LangChain, a full RAG pipeline is ~15 lines: load PDF → chunk → embed → store in Chroma → create retriever → chain with GPT-4. Without it, you'd write 200+ lines of glue code.

### Gotchas & Dev Context
| Framework | Strengths | Watch Out For |
|---|---|---|
| **LangChain** | Huge ecosystem, most tutorials, LCEL syntax | Abstraction complexity, frequent breaking changes |
| **LlamaIndex** | Best for advanced retrieval (multi-vector, KG, agents) | Steeper learning curve |
| **Haystack** | Production-grade pipelines, strong NLP history | Less LLM-focused than the others |

```python
# LangChain RAG in ~10 lines
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA

db = Chroma.from_documents(chunks, OpenAIEmbeddings())
qa = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(), retriever=db.as_retriever(search_kwargs={"k": 5})
)
print(qa.invoke("What is the refund policy?"))
```

### Production FAQ
**Q: Should I use LangChain or LlamaIndex?**
A: LangChain for general RAG + agents + broad integrations. LlamaIndex if your focus is advanced retrieval strategies and complex index types.

**Q: Can I mix frameworks?**
A: Yes — LlamaIndex retrievers can be used inside LangChain chains. Many production systems use both.

**Q: Is it worth going framework-free?**
A: For simple pipelines, frameworks save weeks. For highly customized production systems, the abstraction overhead can become a liability — consider framework-free after you understand the primitives.

---

*End of Batch 10 — RAG & Vector Databases*
