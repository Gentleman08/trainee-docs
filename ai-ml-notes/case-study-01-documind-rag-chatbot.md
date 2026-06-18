# Case Study 1 — DocuMind: RAG-Powered Knowledge Base Chatbot
> A production-grade internal knowledge base chatbot built with RAG, LangChain, Qdrant, and FastAPI.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture Diagrams](#2-architecture-diagrams)
3. [Tech Stack](#3-tech-stack)
4. [Step-by-Step Build](#4-step-by-step-build)
5. [Code Snippets](#5-code-snippets)
6. [Evaluation Strategy](#6-evaluation-strategy)
7. [Cost Analysis](#7-cost-analysis)
8. [Deployment Pipeline](#8-deployment-pipeline)
9. [Production Gotchas](#9-production-gotchas)
10. [Lessons Learned](#10-lessons-learned)

---

## 1. Project Overview

### What Is DocuMind?

**DocuMind** is an internal knowledge base chatbot that allows employees to query company documents using plain English. Instead of manually searching through hundreds of PDFs, Word documents, and Confluence wiki pages, users simply type a question — and DocuMind retrieves the most relevant document sections and synthesises a grounded, cited answer using a large language model (LLM).

It uses **Retrieval-Augmented Generation (RAG)**: a pattern where the LLM is not expected to "know" answers from training data alone. Instead, relevant document chunks are fetched from a vector database at query time and injected into the LLM prompt as context. This keeps answers factual, up-to-date, and traceable to source documents.

### Who Uses It?

| User Type | Use Case |
|---|---|
| **Support engineers** | Instantly look up product specs, runbooks, troubleshooting guides |
| **Sales team** | Find pricing, case studies, compliance docs during calls |
| **HR & Onboarding** | Answer policy, benefits, and process questions for new hires |
| **Developers** | Query internal API docs, architecture decision records (ADRs) |
| **Admins** | Upload new documents, manage sources, view usage analytics |

### The Business Problem

Before DocuMind, a mid-sized software company (~400 employees) faced:

- **Knowledge silos**: Critical information scattered across Confluence, SharePoint, emailed PDFs, and Google Docs.
- **Slow onboarding**: New hires spent 2–3 weeks finding institutional knowledge; senior engineers fielded repetitive questions.
- **Support bottleneck**: Tier-1 support took 4–8 minutes per ticket just locating the relevant runbook.
- **Stale documentation**: Employees couldn't trust search results because they didn't know if docs were current.

DocuMind reduced average time-to-answer from ~6 minutes to under 30 seconds, and dropped "where is the doc for X?" Slack messages by ~60% within the first month of rollout.

---

## 2. Architecture Diagrams

### 2.1 Ingestion Pipeline

This pipeline runs when an admin uploads a new document or when a scheduled sync pulls from Confluence.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          INGESTION PIPELINE                                  │
└──────────────────────────────────────────────────────────────────────────────┘

  ┌──────────┐   ┌──────────┐   ┌──────────┐
  │  PDF     │   │  DOCX    │   │Confluence│
  │ (upload) │   │ (upload) │   │  (sync)  │
  └────┬─────┘   └────┬─────┘   └────┬─────┘
       │              │               │
       └──────────────┴───────────────┘
                       │
                       ▼
             ┌─────────────────┐
             │  Document Queue  │  (Redis / SQS)
             │  (async jobs)   │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │  File Parser    │  PyMuPDF (PDF)
             │                 │  python-docx (DOCX)
             │                 │  Confluence REST API
             └────────┬────────┘
                      │  raw text + metadata
                      ▼
             ┌─────────────────┐
             │  Text Chunker   │  LangChain RecursiveCharacterTextSplitter
             │                 │  chunk_size=512, overlap=64
             └────────┬────────┘
                      │  List[Chunk(text, metadata)]
                      ▼
             ┌─────────────────┐
             │   Embedder      │  OpenAI text-embedding-ada-002
             │                 │  (or local: sentence-transformers)
             └────────┬────────┘
                      │  List[float[1536]]
                      ▼
             ┌─────────────────┐
             │  Vector Store   │  Qdrant (self-hosted or cloud)
             │  (Qdrant)       │  Collection: "documind_docs"
             └────────┬────────┘
                      │  upsert complete
                      ▼
             ┌─────────────────┐
             │  Metadata Store │  PostgreSQL
             │  (PostgreSQL)   │  doc_id, filename, source, chunk_count,
             │                 │  upload_ts, status, checksum
             └─────────────────┘
```

### 2.2 Query / Inference Pipeline

This pipeline runs every time a user asks a question in the chat UI.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          QUERY / INFERENCE PIPELINE                          │
└──────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────┐
  │   User (Browser / Chat UI)  │
  │   "How do I reset 2FA?"     │
  └──────────────┬──────────────┘
                 │  HTTP POST /chat/stream
                 ▼
  ┌─────────────────────────────┐
  │   FastAPI Backend           │
  │   - Auth check (JWT)        │
  │   - Load conversation memory│
  │   - Sanitise input          │
  └──────────────┬──────────────┘
                 │
                 ▼
  ┌─────────────────────────────┐
  │   Query Embedder            │  OpenAI text-embedding-ada-002
  │   question → vector[1536]   │  ~0.3ms
  └──────────────┬──────────────┘
                 │
                 ▼
  ┌─────────────────────────────┐
  │   Qdrant Vector Search      │  top_k=20, cosine similarity
  │   (Approximate NN)          │  optional: filter by source/date
  └──────────────┬──────────────┘
                 │  20 candidate chunks
                 ▼
  ┌─────────────────────────────┐
  │   Reranker                  │  Cohere Rerank v3
  │   (Cross-encoder)           │  or: FlashRank (local, free)
  │                             │  top_k=5 final chunks
  └──────────────┬──────────────┘
                 │  5 high-relevance chunks + scores
                 ▼
  ┌─────────────────────────────┐
  │   Prompt Builder            │  Injects:
  │                             │  - System prompt
  │                             │  - Conversation history (last N turns)
  │                             │  - Retrieved chunks with source labels
  │                             │  - User question
  └──────────────┬──────────────┘
                 │
                 ▼
  ┌─────────────────────────────┐
  │   LLM (GPT-4o / GPT-3.5)   │  OpenAI Chat Completions API
  │   streaming=True            │  temperature=0.2
  └──────────────┬──────────────┘
                 │  token stream (SSE)
                 ▼
  ┌─────────────────────────────┐
  │   Response Streamer         │  Server-Sent Events (SSE)
  │   + Citation Extractor      │  Parses [Source: doc_name, page X]
  └──────────────┬──────────────┘
                 │
                 ▼
  ┌─────────────────────────────┐
  │   User (Browser / Chat UI)  │  Tokens stream in real-time
  │   with clickable citations  │  Citations panel on right sidebar
  └─────────────────────────────┘

  [Side effects]
  ┌────────────────────────────────────────────────────┐
  │  Conversation Memory → Redis (TTL: 24h)            │
  │  Analytics → PostgreSQL (latency, tokens, ratings) │
  │  Feedback → thumbs up/down stored per message      │
  └────────────────────────────────────────────────────┘
```

---

## 3. Tech Stack

| Layer | Technology | Version | Notes |
|---|---|---|---|
| **Document Parsing** | PyMuPDF (`fitz`) | 1.24.x | Best PDF text + layout extraction |
| **Document Parsing** | python-docx | 1.1.x | DOCX paragraph/table extraction |
| **Document Parsing** | `atlassian-python-api` | 3.41.x | Confluence REST API client |
| **Text Chunking** | LangChain | 0.2.x | `RecursiveCharacterTextSplitter` |
| **Embeddings** | OpenAI `text-embedding-ada-002` | API | 1536-dim, $0.0001/1K tokens |
| **Embeddings (alt)** | `sentence-transformers` | 2.7.x | `all-MiniLM-L6-v2` for local dev |
| **Vector Database** | Qdrant | 1.9.x | Self-hosted Docker or Qdrant Cloud |
| **Reranking** | Cohere Rerank v3 | API | Or FlashRank for zero-cost local |
| **LLM** | OpenAI GPT-4o / GPT-3.5-turbo | API | Configurable per tenant |
| **Orchestration** | LangChain LCEL | 0.2.x | Retrieval chain, memory |
| **API Backend** | FastAPI | 0.111.x | Async, streaming SSE support |
| **Task Queue** | Celery + Redis | 5.4.x | Async document ingestion jobs |
| **Metadata DB** | PostgreSQL | 16.x | Doc registry, analytics, users |
| **Session/Cache** | Redis | 7.2.x | Conversation memory, job queues |
| **Frontend** | Next.js 14 | 14.2.x | App Router, streaming UI |
| **Auth** | Auth0 / Supabase Auth | — | JWT tokens, RBAC |
| **Containerisation** | Docker + Docker Compose | 26.x | Local + prod parity |
| **CI/CD** | GitHub Actions | — | Lint, test, build, push, deploy |
| **Cloud (prod)** | AWS ECS Fargate | — | Auto-scaling, no server management |
| **Object Storage** | AWS S3 | — | Original document file store |
| **Monitoring** | LangSmith | — | LLM traces, latency, token usage |
| **Metrics** | Prometheus + Grafana | — | API latency, queue depth, errors |
| **Evaluation** | RAGAS | 0.1.x | Faithfulness, relevance, recall |

---

## 4. Step-by-Step Build

### Phase 1 — Project Setup & Environment

**Goal**: Reproducible local development environment with all services running.

**Steps**:

1. Create the project repository with a clear directory structure.

```
documind/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routers
│   │   ├── core/         # Config, security, logging
│   │   ├── ingestion/    # Parsers, chunker, embedder
│   │   ├── retrieval/    # Query pipeline, reranker
│   │   ├── models/       # SQLAlchemy ORM models
│   │   └── main.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/              # Next.js App Router pages
│   ├── components/       # Chat UI, admin panel
│   └── Dockerfile
├── infra/
│   ├── docker-compose.yml
│   └── github-actions/
└── eval/
    └── ragas_eval.py
```

2. Create a `.env` file for secrets (never commit this):

```bash
OPENAI_API_KEY=sk-...
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=documind_docs
COHERE_API_KEY=...
DATABASE_URL=postgresql://documind:secret@localhost:5432/documind
REDIS_URL=redis://localhost:6379/0
CONFLUENCE_URL=https://yourcompany.atlassian.net
CONFLUENCE_USERNAME=admin@company.com
CONFLUENCE_API_TOKEN=...
AWS_S3_BUCKET=documind-uploads
```

3. Install Python dependencies:

```bash
pip install fastapi uvicorn[standard] langchain langchain-openai langchain-qdrant \
    qdrant-client pymupdf python-docx atlassian-python-api openai cohere \
    celery redis sqlalchemy asyncpg alembic python-multipart pydantic-settings \
    ragas flashrank sentence-transformers python-jose passlib
```

4. Spin up local services with Docker Compose:

```bash
docker compose up -d qdrant postgres redis
```

5. Initialise the Qdrant collection and run Alembic migrations:

```bash
python -m app.core.init_qdrant   # creates collection with cosine distance
alembic upgrade head              # creates tables in PostgreSQL
```

---

### Phase 2 — Ingestion Pipeline

**Goal**: Parse, chunk, embed, and store documents so they can be retrieved later.

**Key decisions made**:
- **Chunk size = 512 tokens, overlap = 64 tokens**: Balances context richness vs. retrieval precision. Larger chunks risk irrelevant text diluting the context; smaller chunks lose surrounding context.
- **Metadata stored per chunk**: `doc_id`, `source`, `page`, `section_title`, `upload_date`. This enables filtered search (e.g. "only search 2024 HR docs").
- **Idempotency via SHA-256 checksum**: Re-uploading the same file doesn't create duplicate vectors.

**Steps**:

1. Parse raw bytes from PDF / DOCX / Confluence into clean text strings.
2. Split text into overlapping chunks using `RecursiveCharacterTextSplitter`.
3. Batch-embed chunks using the OpenAI embeddings API (max 2048 inputs per call).
4. Upsert vectors + metadata into Qdrant.
5. Record the document in PostgreSQL with status `completed`.

See detailed code in [Section 5](#5-code-snippets).

---

### Phase 3 — Query Pipeline

**Goal**: Turn a user question into a grounded, cited LLM answer.

**Key decisions made**:
- **Retrieve top-20, rerank to top-5**: Over-fetching and reranking significantly improves answer quality compared to taking top-5 directly from vector search (a pure bi-encoder tends to be noisier).
- **Conversation memory in Redis**: Stores last 6 turns (3 user + 3 assistant), injected into every prompt. Keeps context window manageable.
- **Temperature = 0.2**: Low temperature reduces hallucination while still allowing natural language generation.
- **Strict system prompt**: Instructs the model to only answer from provided context and say "I don't know" if context is insufficient.

**Steps**:

1. Embed the user's question with the same model used during ingestion.
2. Search Qdrant for top-20 nearest neighbours (cosine similarity).
3. Pass candidates through Cohere Rerank v3 to get top-5 scored chunks.
4. Build a prompt: `system_prompt + history + context_chunks + question`.
5. Stream response from OpenAI API via SSE.
6. Parse citation markers `[Source: filename, p.X]` from the response for the UI.

---

### Phase 4 — FastAPI Backend

**Goal**: Expose ingestion and query functionality as a secure REST + SSE API.

**Endpoints**:

| Method | Path | Description |
|---|---|---|
| `POST` | `/documents/upload` | Admin uploads a file → triggers async ingestion job |
| `GET` | `/documents` | List all documents with status + metadata |
| `DELETE` | `/documents/{doc_id}` | Remove document + its vectors from Qdrant |
| `POST` | `/chat/stream` | Query endpoint, returns SSE token stream |
| `GET` | `/chat/history/{session_id}` | Fetch conversation history |
| `POST` | `/feedback` | Store thumbs up/down rating for a message |
| `GET` | `/analytics/summary` | Admin dashboard stats |

**Auth**: JWT validation via Auth0. Admin-only endpoints require `role: admin` claim.

---

### Phase 5 — Frontend (Next.js 14)

**Goal**: A polished chat UI with streaming support and an admin document panel.

**Key UI features**:
- **Streaming chat**: Uses the `useChat` hook from the `ai` SDK (Vercel AI SDK) which natively handles SSE token streaming.
- **Citation sidebar**: Each answer shows the source document(s) as clickable cards that link to the original file in S3.
- **Admin panel**: Drag-and-drop file upload, document list with status indicators (processing / ready / failed), delete button.
- **Session continuity**: Conversation stored in `localStorage` keyed by session UUID, synced to Redis on the backend.

---

### Phase 6 — Deployment

**Goal**: Production-grade deployment with auto-scaling, CI/CD, and observability.

See [Section 8](#8-deployment-pipeline) for Dockerfiles, Compose, and GitHub Actions YAML.

**Deployment targets**:
- **Qdrant**: Qdrant Cloud (managed) or self-hosted on a dedicated EC2 instance with EBS volume for persistence.
- **FastAPI backend**: AWS ECS Fargate (serverless containers) behind an ALB.
- **Frontend**: Vercel (easiest) or S3 + CloudFront.
- **PostgreSQL**: AWS RDS PostgreSQL.
- **Redis**: AWS ElastiCache Redis.
- **Celery workers**: Separate ECS task definition, auto-scaled by queue depth (SQS + CloudWatch).

---

## 5. Code Snippets

### 5.1 Document Loader

```python
# backend/app/ingestion/loaders.py
"""
Loaders for PDF, DOCX, and Confluence sources.
Returns a list of dicts: {"text": str, "metadata": dict}
"""
import hashlib
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF — pip install pymupdf
from docx import Document  # pip install python-docx
from atlassian import Confluence  # pip install atlassian-python-api


def load_pdf(file_bytes: bytes, filename: str) -> list[dict]:
    """
    Extract text from a PDF, page by page.
    Preserves page numbers in metadata for citations.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")  # plain text; use "blocks" for layout
        if text.strip():  # skip blank/image-only pages
            pages.append({
                "text": text,
                "metadata": {
                    "source": filename,
                    "page": page_num + 1,
                    "doc_type": "pdf",
                    "checksum": hashlib.sha256(file_bytes).hexdigest(),
                }
            })
    doc.close()
    return pages


def load_docx(file_bytes: bytes, filename: str) -> list[dict]:
    """
    Extract paragraphs and tables from a DOCX file.
    Headings become section_title metadata for richer context.
    """
    import io
    document = Document(io.BytesIO(file_bytes))
    sections = []
    current_heading = "Introduction"
    buffer = []

    for para in document.paragraphs:
        # Detect Word heading styles (Heading 1, Heading 2, etc.)
        if para.style.name.startswith("Heading"):
            if buffer:
                sections.append({
                    "text": "\n".join(buffer),
                    "metadata": {
                        "source": filename,
                        "section_title": current_heading,
                        "doc_type": "docx",
                        "checksum": hashlib.sha256(file_bytes).hexdigest(),
                    }
                })
                buffer = []
            current_heading = para.text.strip()
        else:
            text = para.text.strip()
            if text:
                buffer.append(text)

    # Flush remaining buffer
    if buffer:
        sections.append({
            "text": "\n".join(buffer),
            "metadata": {
                "source": filename,
                "section_title": current_heading,
                "doc_type": "docx",
                "checksum": hashlib.sha256(file_bytes).hexdigest(),
            }
        })
    return sections


def load_confluence_page(page_id: str, confluence_client: Confluence) -> list[dict]:
    """
    Fetch a Confluence page and return its body as a single document.
    Uses the storage format → strips HTML tags to get plain text.
    """
    import re

    page = confluence_client.get_page_by_id(
        page_id,
        expand="body.storage,version,space"
    )
    html_body = page["body"]["storage"]["value"]

    # Strip HTML tags — for production, use BeautifulSoup instead
    plain_text = re.sub(r"<[^>]+>", " ", html_body)
    plain_text = re.sub(r"\s+", " ", plain_text).strip()

    return [{
        "text": plain_text,
        "metadata": {
            "source": f"Confluence: {page['title']}",
            "page_id": page_id,
            "space": page["space"]["key"],
            "doc_type": "confluence",
            "url": page["_links"]["webui"],
        }
    }]
```

---

### 5.2 Text Chunker

```python
# backend/app/ingestion/chunker.py
"""
Splits loaded document sections into overlapping chunks.
Uses LangChain's RecursiveCharacterTextSplitter for intelligent splitting.
"""
from langchain.text_splitter import RecursiveCharacterTextSplitter


def chunk_documents(
    documents: list[dict],
    chunk_size: int = 512,
    chunk_overlap: int = 64,
) -> list[dict]:
    """
    Takes output from a loader (list of {text, metadata}) and splits each
    section into smaller, overlapping chunks.

    chunk_size: approx characters per chunk (~512 chars ≈ 128 tokens)
    chunk_overlap: characters shared between adjacent chunks — prevents
                   important sentences from being cut at a boundary
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        # Tries to split on paragraphs first, then sentences, then words
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,  # character-based; swap for tiktoken token-based
    )

    chunks = []
    for doc in documents:
        texts = splitter.split_text(doc["text"])
        for i, text in enumerate(texts):
            chunks.append({
                "text": text,
                "metadata": {
                    **doc["metadata"],   # preserve all original metadata
                    "chunk_index": i,    # position within the original section
                    "chunk_total": len(texts),
                }
            })

    return chunks
```

---

### 5.3 Embedding & Upsert to Qdrant

```python
# backend/app/ingestion/embedder.py
"""
Embeds document chunks and upserts them into Qdrant.
Uses OpenAI text-embedding-ada-002 (1536 dimensions).
Batches requests to stay within API rate limits.
"""
import uuid
from typing import Iterator

from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    UpdateStatus,
)

openai_client = OpenAI()  # reads OPENAI_API_KEY from environment
qdrant = QdrantClient(host="localhost", port=6333)

COLLECTION_NAME = "documind_docs"
EMBEDDING_MODEL = "text-embedding-ada-002"
EMBEDDING_DIM = 1536
BATCH_SIZE = 100  # OpenAI allows up to 2048 inputs, but smaller = safer


def ensure_collection_exists():
    """Create Qdrant collection if it doesn't exist yet."""
    existing = [c.name for c in qdrant.get_collections().collections]
    if COLLECTION_NAME not in existing:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_DIM,
                distance=Distance.COSINE,  # cosine works well for text
            ),
        )
        print(f"Created Qdrant collection: {COLLECTION_NAME}")


def _batched(items: list, size: int) -> Iterator[list]:
    """Yield successive batches from a list."""
    for i in range(0, len(items), size):
        yield items[i : i + size]


def embed_and_upsert(chunks: list[dict], doc_id: str) -> int:
    """
    Embed a list of text chunks and upsert them into Qdrant.

    Returns the number of vectors successfully upserted.

    Each Qdrant point contains:
      - id: UUID (deterministic from doc_id + chunk_index to support re-runs)
      - vector: float[1536] embedding
      - payload: all metadata + original text (for display in citations)
    """
    ensure_collection_exists()
    total_upserted = 0

    for batch in _batched(chunks, BATCH_SIZE):
        texts = [chunk["text"] for chunk in batch]

        # Call OpenAI Embeddings API
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts,
        )
        embeddings = [item.embedding for item in response.data]

        # Build Qdrant PointStructs
        points = []
        for chunk, embedding in zip(batch, embeddings):
            # Deterministic ID: same chunk from same doc always gets same UUID
            # This enables idempotent re-indexing without duplicates
            point_id = str(uuid.uuid5(
                uuid.NAMESPACE_DNS,
                f"{doc_id}_{chunk['metadata']['chunk_index']}"
            ))
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        **chunk["metadata"],
                        "text": chunk["text"],  # store text for display
                        "doc_id": doc_id,
                    },
                )
            )

        result = qdrant.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )
        assert result.status == UpdateStatus.COMPLETED
        total_upserted += len(points)

    return total_upserted
```

---

### 5.4 RAG Retrieval Chain (LangChain LCEL)

```python
# backend/app/retrieval/chain.py
"""
Full RAG retrieval chain using LangChain Expression Language (LCEL).
Supports multi-turn conversation via Redis-backed memory.
"""
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from qdrant_client import QdrantClient
import cohere

COLLECTION_NAME = "documind_docs"
REDIS_URL = "redis://localhost:6379/0"

# ── LLM ──────────────────────────────────────────────────────────────────────
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.2,       # low = more factual, less creative
    streaming=True,        # enables token-by-token streaming
    max_tokens=1024,
)

# ── Embeddings (must match ingestion model) ───────────────────────────────────
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

# ── Vector Store ──────────────────────────────────────────────────────────────
qdrant_client = QdrantClient(host="localhost", port=6333)
vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings,
)

# Retrieve top-20 candidates before reranking
base_retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 20},
)

# ── Reranker (Cohere) ─────────────────────────────────────────────────────────
cohere_client = cohere.Client()  # reads COHERE_API_KEY from env

def rerank(query: str, documents: list) -> list:
    """
    Use Cohere Rerank v3 to reorder the top-20 retrieved docs.
    Returns only the top 5 most relevant, in ranked order.
    """
    doc_texts = [doc.page_content for doc in documents]
    response = cohere_client.rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=doc_texts,
        top_n=5,
    )
    # Map ranked indices back to original Document objects
    return [documents[hit.index] for hit in response.results]


# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are DocuMind, an expert assistant for our company's \
internal knowledge base.

RULES:
1. Answer ONLY using the provided context. Do NOT use prior knowledge.
2. If the context does not contain enough information to answer confidently, \
say: "I don't have enough information in the current documents to answer this."
3. Always cite your source at the end of each factual statement using the \
format: [Source: <document name>, p.<page>] or [Source: <document name>, \
section: <section title>].
4. Be concise and direct. Use bullet points for lists.
5. Never fabricate document names, page numbers, or statistics.

Context:
{context}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder("chat_history"),   # multi-turn memory injected here
    ("human", "{input}"),
])

# ── Chain Assembly ────────────────────────────────────────────────────────────
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(base_retriever, question_answer_chain)


def get_session_history(session_id: str) -> RedisChatMessageHistory:
    """
    Returns a Redis-backed message history for a given session.
    TTL = 86400s (24 hours) — old conversations auto-expire.
    """
    return RedisChatMessageHistory(
        session_id=session_id,
        url=REDIS_URL,
        ttl=86400,
        key_prefix="documind:history:",
    )


# Wrap the chain to automatically inject + update conversation history
conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)


async def query_with_rerank(question: str, session_id: str):
    """
    Full query pipeline with reranking.
    Yields answer tokens as they stream from the LLM.

    Note: Because LangChain's built-in retriever doesn't expose a hook for
    post-retrieval reranking in LCEL, we manually retrieve → rerank → stuff.
    """
    # Step 1: Retrieve candidates
    docs = base_retriever.invoke(question)

    # Step 2: Rerank to top 5
    reranked_docs = rerank(question, docs)

    # Step 3: Format context string for the prompt
    context_str = "\n\n---\n\n".join(
        f"[Source: {doc.metadata.get('source', 'Unknown')}, "
        f"p.{doc.metadata.get('page', 'N/A')}]\n{doc.page_content}"
        for doc in reranked_docs
    )

    # Step 4: Build and stream from prompt
    history = get_session_history(session_id)
    chain_input = {
        "input": question,
        "context": context_str,
        "chat_history": history.messages,
    }

    full_response = ""
    async for chunk in llm.astream(
        prompt.format_messages(**chain_input)
    ):
        token = chunk.content
        full_response += token
        yield token  # stream to the HTTP response

    # Step 5: Persist turn to memory
    history.add_user_message(question)
    history.add_ai_message(full_response)
```

---

### 5.5 FastAPI Streaming Endpoint

```python
# backend/app/api/chat.py
"""
FastAPI router for the chat endpoint.
Uses Server-Sent Events (SSE) to stream LLM tokens to the browser.
"""
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.retrieval.chain import query_with_rerank
from app.core.security import get_current_user  # JWT validator

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    question: str
    session_id: str  # UUID, generated by client on first load


@router.post("/stream")
async def chat_stream(
    body: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Accepts a user question and streams the LLM response as SSE.

    SSE format expected by the client:
      data: {"token": "Hello"}
      data: {"token": " world"}
      data: [DONE]
    """
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Sanitise: simple length guard (real app should add PII scrubbing too)
    if len(body.question) > 2000:
        raise HTTPException(status_code=400, detail="Question too long (max 2000 chars).")

    async def event_generator():
        try:
            async for token in query_with_rerank(
                question=body.question,
                session_id=body.session_id,
            ):
                # Each SSE event is a JSON object wrapped in "data: ...\n\n"
                payload = json.dumps({"token": token})
                yield f"data: {payload}\n\n"
        except Exception as e:
            # Send error event so client can display a friendly message
            error_payload = json.dumps({"error": str(e)})
            yield f"data: {error_payload}\n\n"
        finally:
            # Signal end of stream
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable nginx buffering for SSE
        },
    )


@router.get("/history/{session_id}")
async def get_history(
    session_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Return conversation history for a session (last 20 messages)."""
    from langchain_community.chat_message_histories import RedisChatMessageHistory
    from app.core.config import settings

    history = RedisChatMessageHistory(
        session_id=session_id,
        url=settings.REDIS_URL,
        key_prefix="documind:history:",
    )
    messages = [
        {"role": msg.type, "content": msg.content}
        for msg in history.messages[-20:]  # last 10 turns
    ]
    return {"session_id": session_id, "messages": messages}
```

---

### 5.6 Celery Ingestion Worker

```python
# backend/app/ingestion/tasks.py
"""
Celery async tasks for document ingestion.
Triggered when an admin uploads a file via the API.
"""
from celery import Celery
from app.ingestion.loaders import load_pdf, load_docx
from app.ingestion.chunker import chunk_documents
from app.ingestion.embedder import embed_and_upsert
from app.models.document import update_document_status  # SQLAlchemy helper
import boto3
import hashlib

celery_app = Celery("documind", broker="redis://localhost:6379/0")
s3 = boto3.client("s3")


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def ingest_document(self, doc_id: str, s3_key: str, filename: str):
    """
    Full ingestion pipeline run as an async Celery task.

    Workflow:
    1. Download file from S3
    2. Parse (PDF or DOCX)
    3. Chunk
    4. Embed + upsert to Qdrant
    5. Update doc status in PostgreSQL
    """
    try:
        update_document_status(doc_id, "processing")

        # 1. Download from S3
        obj = s3.get_object(Bucket="documind-uploads", Key=s3_key)
        file_bytes = obj["Body"].read()

        # 2. Parse based on file extension
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext == "pdf":
            pages = load_pdf(file_bytes, filename)
        elif ext in ("docx", "doc"):
            pages = load_docx(file_bytes, filename)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        # 3. Chunk
        chunks = chunk_documents(pages, chunk_size=512, chunk_overlap=64)

        # 4. Embed + upsert
        total = embed_and_upsert(chunks, doc_id=doc_id)

        # 5. Mark as ready
        update_document_status(doc_id, "ready", chunk_count=total)

    except Exception as exc:
        update_document_status(doc_id, "failed", error=str(exc))
        # Retry up to 3 times with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 30)
```

---

## 6. Evaluation Strategy

### 6.1 Why Evaluation Matters for RAG

RAG systems can fail in subtle ways:
- The retrieved chunks are correct, but the LLM ignores them (hallucination).
- The chunks are retrieved, but they're the wrong ones (retrieval failure).
- The answer is factually correct but doesn't cite sources accurately.

Manual review is too slow at scale. We use the **RAGAS** framework for automated evaluation.

### 6.2 RAGAS Metrics

| Metric | What It Measures | Target Score |
|---|---|---|
| **Faithfulness** | Does the answer contain claims NOT in the retrieved context? | > 0.85 |
| **Answer Relevancy** | Is the answer actually responsive to the question asked? | > 0.80 |
| **Context Recall** | What % of the ground-truth answer can be found in retrieved context? | > 0.75 |
| **Context Precision** | What fraction of retrieved chunks were actually useful? | > 0.70 |

### 6.3 Running RAGAS Evaluation

```python
# eval/ragas_eval.py
"""
Runs RAGAS evaluation on a test dataset.
Dataset format: questions with ground truth answers and reference contexts.
"""
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# ── Build evaluation dataset ──────────────────────────────────────────────────
# In practice, use ~50–100 hand-labelled Q&A pairs from real users.
eval_samples = [
    {
        "question": "What is the process to reset a user's 2FA?",
        "answer": "",          # filled by running inference
        "contexts": [],        # filled by running retrieval
        "ground_truth": (
            "To reset 2FA: go to Admin → Users → select the user "
            "→ click 'Reset 2FA'. The user will be prompted on next login."
        ),
    },
    # ... add 49+ more samples
]

# ── Run inference to fill answers + contexts ──────────────────────────────────
from app.retrieval.chain import query_with_rerank, base_retriever

for sample in eval_samples:
    docs = base_retriever.invoke(sample["question"])
    sample["contexts"] = [doc.page_content for doc in docs[:5]]
    # For evaluation, run non-streaming inference
    # (simplified — in practice batch this)
    sample["answer"] = "..."  # run your chain here

# ── Evaluate ──────────────────────────────────────────────────────────────────
dataset = Dataset.from_list(eval_samples)

results = evaluate(
    dataset=dataset,
    metrics=[faithfulness, answer_relevancy, context_recall, context_precision],
    llm=ChatOpenAI(model="gpt-4o"),
    embeddings=OpenAIEmbeddings(model="text-embedding-ada-002"),
)

print(results)
# Output example:
# {'faithfulness': 0.89, 'answer_relevancy': 0.83,
#  'context_recall': 0.77, 'context_precision': 0.72}

# Save detailed results for analysis
results.to_pandas().to_csv("eval/ragas_results.csv", index=False)
```

### 6.4 Measuring Hallucination Rate

Faithfulness score directly approximates hallucination rate: `hallucination_rate = 1 - faithfulness`.

For a more targeted check, run a separate "claim verification" pass:

```python
# eval/hallucination_check.py
"""
For each answer, extract factual claims and verify against retrieved context.
Uses GPT-4o as a judge (cheap, fast, reasonably accurate).
"""
from openai import OpenAI

client = OpenAI()

VERIFY_PROMPT = """
You are a fact-checker. Given the following retrieved context and an AI answer,
identify any claim in the answer that is NOT supported by the context.

Context:
{context}

AI Answer:
{answer}

List unsupported claims as bullet points. If all claims are supported, say "ALL SUPPORTED".
"""

def check_hallucination(answer: str, context: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # cheaper model fine for judge tasks
        messages=[
            {"role": "user", "content": VERIFY_PROMPT.format(
                context=context, answer=answer
            )}
        ],
        temperature=0,
    )
    return response.choices[0].message.content
```

### 6.5 A/B Testing Retrieval Strategies

Run weekly evaluation sweeps comparing:
- **Baseline**: top-5 vector search only
- **Variant A**: top-20 + Cohere rerank
- **Variant B**: top-20 + FlashRank (local)
- **Variant C**: Hybrid search (dense + BM25 sparse)

Track faithfulness + user thumbs-up rate. Use the variant with highest combined score.

---

## 7. Cost Analysis

### 7.1 Embedding Costs (Ingestion)

**OpenAI `text-embedding-ada-002`**: $0.0001 per 1,000 tokens

| Document Volume | Estimated Tokens | Embedding Cost |
|---|---|---|
| 100 PDFs (~500 pages) | ~2.5M tokens | **$0.25** |
| 1,000 PDFs (~5,000 pages) | ~25M tokens | **$2.50** |
| 10,000 PDFs | ~250M tokens | **$25.00** |

Initial ingestion is effectively free. Re-ingestion after model change is the main cost event.

### 7.2 LLM Token Costs (Per Query)

Each query consumes:
- ~1,500 tokens context (5 chunks × ~300 tokens avg)
- ~200 tokens system prompt + history
- ~350 tokens answer output

**Total: ~2,050 tokens per query**

| Model | Input ($/1M) | Output ($/1M) | Cost/Query | Queries/Month | Monthly Cost |
|---|---|---|---|---|---|
| **GPT-3.5-turbo** | $0.50 | $1.50 | ~$0.0016 | 10,000 | **$16** |
| **GPT-4o** | $5.00 | $15.00 | ~$0.015 | 10,000 | **$150** |
| **GPT-4o** | $5.00 | $15.00 | ~$0.015 | 50,000 | **$750** |

> **Recommendation**: Start with GPT-3.5-turbo for general queries. Route complex queries (detected by confidence score or user escalation) to GPT-4o. This hybrid approach reduces costs by ~70% vs all-GPT-4o.

### 7.3 Reranking Costs (Cohere)

**Cohere Rerank v3**: $1.00 per 1,000 queries (as of 2024)

| Queries/Month | Monthly Cost |
|---|---|
| 10,000 | $10 |
| 50,000 | $50 |

Alternative: **FlashRank** (local Python library, zero API cost, ~90% of Cohere quality).

### 7.4 Qdrant Hosting

| Option | Cost | Best For |
|---|---|---|
| **Self-hosted (Docker)** | Free (infra cost only) | Dev / small teams |
| **Qdrant Cloud Free Tier** | Free (1GB RAM, 1 node) | Prototyping (~500K vectors) |
| **Qdrant Cloud Starter** | ~$25/month | Up to 5M vectors |
| **Qdrant Cloud Scale** | ~$75–200/month | Production, multi-tenant |
| **Self-hosted EC2 (r6i.large)** | ~$120/month | Large volume, full control |

### 7.5 Full Monthly Cost Estimate (10,000 queries/month)

| Component | Monthly Cost |
|---|---|
| OpenAI Embeddings (new docs only) | ~$0.50 |
| GPT-4o LLM calls | ~$150 |
| Cohere Rerank | ~$10 |
| Qdrant Cloud Starter | ~$25 |
| AWS ECS Fargate (2 tasks) | ~$30 |
| AWS RDS PostgreSQL (db.t3.small) | ~$25 |
| AWS ElastiCache Redis (cache.t3.micro) | ~$15 |
| **Total** | **~$255/month** |

At 10,000 queries/month per 400 employees, that's **~$0.025 per query** — significantly cheaper than a Tier-1 support ticket.

---

## 8. Deployment Pipeline

### 8.1 Dockerfile (FastAPI Backend)

```dockerfile
# backend/Dockerfile
# Multi-stage build: smaller final image, no build tools in production

# ── Stage 1: Build dependencies ───────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build deps for packages with C extensions (psycopg2, pymupdf)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Production image ─────────────────────────────────────────────────
FROM python:3.11-slim AS production

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Copy application source
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Non-root user for security
RUN useradd --no-create-home --shell /bin/false appuser
USER appuser

EXPOSE 8000

# Run with Uvicorn; in prod use gunicorn + uvicorn workers for multi-process
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "2", "--loop", "uvloop", "--http", "httptools"]
```

---

### 8.2 docker-compose.yml (Local Development)

```yaml
# infra/docker-compose.yml
version: "3.9"

services:

  # ── Qdrant Vector Database ──────────────────────────────────────────────────
  qdrant:
    image: qdrant/qdrant:v1.9.2
    ports:
      - "6333:6333"   # HTTP API
      - "6334:6334"   # gRPC API
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      QDRANT__SERVICE__GRPC_PORT: 6334

  # ── PostgreSQL ──────────────────────────────────────────────────────────────
  postgres:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: documind
      POSTGRES_USER: documind
      POSTGRES_PASSWORD: secret
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # ── Redis (memory + task queue) ─────────────────────────────────────────────
  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes  # persist to disk
    volumes:
      - redis_data:/data

  # ── FastAPI Backend ─────────────────────────────────────────────────────────
  api:
    build:
      context: ./backend
      target: production
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - qdrant
      - postgres
      - redis
    volumes:
      - ./backend/app:/app/app  # hot-reload in dev (remove in prod)

  # ── Celery Worker (Ingestion) ───────────────────────────────────────────────
  worker:
    build:
      context: ./backend
      target: production
    command: celery -A app.ingestion.tasks worker --loglevel=info --concurrency=2
    env_file: .env
    depends_on:
      - redis
      - postgres
      - qdrant

  # ── Frontend (Next.js) ──────────────────────────────────────────────────────
  frontend:
    build:
      context: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000

volumes:
  qdrant_data:
  postgres_data:
  redis_data:
```

---

### 8.3 GitHub Actions CI/CD Workflow

```yaml
# .github/workflows/deploy.yml
name: CI/CD — DocuMind

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: documind-api
  ECS_CLUSTER: documind-cluster
  ECS_SERVICE: documind-api-service
  CONTAINER_NAME: documind-api

jobs:
  # ── Job 1: Lint & Test ──────────────────────────────────────────────────────
  test:
    runs-on: ubuntu-latest
    services:
      redis:
        image: redis:7.2-alpine
        ports: ["6379:6379"]
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: documind_test
          POSTGRES_USER: documind
          POSTGRES_PASSWORD: secret
        ports: ["5432:5432"]
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install dependencies
        run: pip install -r backend/requirements.txt pytest pytest-asyncio httpx

      - name: Run linting
        run: |
          pip install ruff
          ruff check backend/app/

      - name: Run tests
        env:
          DATABASE_URL: postgresql://documind:secret@localhost:5432/documind_test
          REDIS_URL: redis://localhost:6379/0
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: pytest backend/tests/ -v --tb=short

  # ── Job 2: Build & Push to ECR ─────────────────────────────────────────────
  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'  # only deploy from main
    outputs:
      image: ${{ steps.build-image.outputs.image }}

    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build, tag, and push image to ECR
        id: build-image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG \
            --target production backend/
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT

  # ── Job 3: Deploy to ECS ────────────────────────────────────────────────────
  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Download current ECS task definition
        run: |
          aws ecs describe-task-definition \
            --task-definition documind-api \
            --query taskDefinition > task-def.json

      - name: Update image in task definition
        id: task-def
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: task-def.json
          container-name: ${{ env.CONTAINER_NAME }}
          image: ${{ needs.build-and-push.outputs.image }}

      - name: Deploy to ECS
        uses: aws-actions/amazon-ecs-deploy-task-definition@v1
        with:
          task-definition: ${{ steps.task-def.outputs.task-definition }}
          service: ${{ env.ECS_SERVICE }}
          cluster: ${{ env.ECS_CLUSTER }}
          wait-for-service-stability: true  # block until healthy
```

---

### 8.4 Azure App Service Alternative

For teams on Azure, replace the ECS deployment step with:

```bash
# Deploy Docker image to Azure App Service
az webapp config container set \
  --name documind-api \
  --resource-group documind-rg \
  --docker-custom-image-name $ACR_REGISTRY/documind-api:$IMAGE_TAG \
  --docker-registry-server-url https://$ACR_REGISTRY \
  --docker-registry-server-user $ACR_USERNAME \
  --docker-registry-server-password $ACR_PASSWORD

az webapp restart --name documind-api --resource-group documind-rg
```

---

## 9. Production Gotchas

These are real issues we hit in production — not theoretical edge cases.

- **🔴 PDF text extraction is never perfect.** Scanned PDFs return empty text (they're images). Documents with complex multi-column layouts, tables, or rotated text lose structure when parsed by PyMuPDF. Fix: detect image-only PDFs with `page.get_text() == ""` and route them through an OCR step (Tesseract via `pytesseract`, or AWS Textract for better quality). Tables need special handling — extract with `page.find_tables()` and convert to markdown before chunking.

- **🔴 Chunking at fixed character sizes breaks sentences mid-word across a paragraph boundary.** This confuses the embedder and reduces retrieval quality. Fix: always use `RecursiveCharacterTextSplitter` (not `CharacterTextSplitter`), which prefers splitting on paragraph breaks and sentence endings. Also, tune `chunk_size` based on your average document style — technical docs need smaller chunks (~300 tokens) than narrative docs (~600 tokens).

- **🔴 Embedding model version drift.** If you switch from `ada-002` to a newer model (e.g., `text-embedding-3-large`), all existing vectors become **incompatible** — cosine similarity between old and new embeddings is meaningless. Fix: version your Qdrant collection name (`documind_docs_v2`), re-index everything before switching traffic, then delete the old collection. Build a migration script, not a manual process.

- **🔴 Context window overflow with long conversations.** By turn 10+, the accumulated conversation history + system prompt + context chunks can exceed the model's context limit (128K tokens for GPT-4o, 16K for GPT-3.5-turbo). Fix: summarise old history using an LLM every N turns rather than injecting raw message history. LangChain's `ConversationSummaryBufferMemory` handles this.

- **🔴 Qdrant cold start on small instances.** On low-memory machines (< 4GB RAM), Qdrant loads the entire vector index into memory and can OOM-crash under concurrent load. Fix: use Qdrant's `on_disk_payload=True` option to store payloads on disk instead of RAM, and set `m=16, ef_construct=100` in HNSW index config to trade some recall for lower memory usage.

- **🔴 Celery tasks silently fail on large PDFs.** A 500-page PDF can take 3–4 minutes to ingest, causing Celery's soft time limit to kill the task mid-embedding, leaving the document in `processing` state forever. Fix: set `soft_time_limit=300, time_limit=360` on the task, add a dead-letter queue to catch killed tasks, and run a cron job that resets documents stuck in `processing` for > 10 minutes.

- **🔴 Duplicate vectors from re-uploads.** Without idempotency checks, uploading the same PDF twice doubles the vector count and causes the same chunk to appear twice in retrieval results, artificially boosting its relevance score. Fix: compute a SHA-256 checksum of the raw file bytes on upload. If the checksum already exists in PostgreSQL, skip ingestion and return the existing `doc_id`. Use deterministic UUIDs (UUID v5) as Qdrant point IDs so re-indexing naturally overwrites existing points.

- **🔴 LLM latency spikes during OpenAI outages.** OpenAI has periodic degraded performance windows (check status.openai.com). Without fallback handling, your chat endpoint just times out. Fix: implement a circuit breaker pattern (using `tenacity` for retries with exponential backoff), and optionally fall back to a local model (Ollama + LLaMA 3) during outages. Set a 30-second timeout on all OpenAI API calls.

- **🔴 SSE connections drop under nginx without `X-Accel-Buffering: no`.** Nginx buffers responses by default. For SSE streaming, this means the entire response is held in nginx's buffer until the LLM finishes generating — completely defeating the purpose of streaming. Fix: add `X-Accel-Buffering: no` to the response headers from FastAPI (already included in the code above) and add `proxy_buffering off;` to your nginx config.

- **🔴 Sensitive document content leaking between users.** If access control isn't enforced at the vector retrieval layer, a user in the Engineering department can retrieve chunks from an HR-only salary document. Fix: use Qdrant's **payload filters** to tag each vector with a `permissions` field (e.g., `["hr", "all"]`) and filter by the current user's role at search time. This adds minimal latency but is critical for compliance.

---

## 10. Lessons Learned

### What Worked Well

**Reranking made a bigger difference than expected.** Moving from top-5 direct vector search to top-20 + Cohere rerank improved faithfulness scores by ~12 percentage points in our RAGAS evaluation. The additional ~50ms latency was completely invisible to users. We should have added this on day one instead of treating it as a later optimisation.

**Streaming responses changed user perception of speed.** Before implementing SSE streaming, users saw a 4–8 second blank screen, then a full answer appeared. After streaming, the first token appears in ~800ms. Despite the total latency being similar, users rated the experience as "much faster." Perceived latency matters more than actual latency.

**Storing the raw chunk text inside Qdrant payloads simplified the stack.** We initially stored chunk text only in PostgreSQL and fetched it on every retrieval. This added a round-trip DB query on every search. Moving text into Qdrant payloads eliminated the join and reduced p95 query latency by ~40ms.

**Confluence sync added more business value than expected.** Users cared far more about searching live Confluence pages than static PDFs. Confluence content is updated frequently, and employees trusted answers sourced from Confluence more than from uploaded PDFs (which might be stale). Invest in live sync integrations early.

### What We'd Do Differently

**We underestimated the diversity of PDF layouts.** We assumed most PDFs would be text-based and cleanly parseable. In reality, ~20% of the company's documents were scanned images, and another 15% had complex table/form layouts that required special handling. We should have profiled the document corpus before choosing a parser.

**Chunk size should have been tuned per document type from the start.** Using a single chunk size (512 chars) for all documents worked "okay" but wasn't optimal for any of them. Technical API docs needed smaller chunks (~200 chars) to keep code snippets intact; legal policies needed larger chunks (~800 chars) to preserve clause context. Document-type-aware chunking would have improved retrieval quality from day one.

**We built the admin panel too late.** The admin UI for uploading documents and monitoring ingestion status was treated as low priority. As a result, engineers had to manually run ingestion scripts for the first two months, which created bottlenecks and frustrated non-technical stakeholders. Build admin tooling early — it pays for itself immediately.

**LangChain abstraction hid performance bottlenecks.** Early on, we used high-level LangChain chains for everything. When profiling revealed slow retrieval, it was hard to see exactly which step was slow because LangChain's abstraction layers obscured the call graph. We switched to LangChain Expression Language (LCEL) with LangSmith tracing enabled from the start, which gave us per-step latency visibility. Use tracing from day zero.

**Evaluation was bolted on, not built in.** We launched to 50 users before running a single RAGAS evaluation. Several weeks later, we discovered our faithfulness score was only 0.71 — meaning ~29% of answers contained claims not in the retrieved context. We had to retrospectively fix the system prompt and add the reranker to bring it above 0.85. Run evaluation against a golden dataset before first user access, and run it weekly thereafter.

---

*Case study written May 2026. Library versions referenced are current as of that date. Always check the official docs for the latest API changes.*
