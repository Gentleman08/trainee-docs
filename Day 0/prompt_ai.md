# PROMPT — AI & Machine Learning Notes

Write me new notes on AI & Machine Learning in a new directory such that it explains each of the term below in beginner friendly language.

For each term:
- Write real world development example
- ASCII diagram if applicable
- Add gotchas and developer-related context
- Add production scenario based FAQ

Additionally, after the glossary, write **2 full project case studies** (described at the bottom) with architecture, code snippets, deployment steps, and lessons learned.

Write me a markdown file with index at the starting, create it by yourself after analysing the content. If required divide the notes generation into batches and maintain a batch file to continue from next batch if context window is finished.

Also make the notes as short as possible without degrading quality and without degrading beginner friendly language.

---

## PART 1 — Complete AI & ML Glossary

### Batch 1 — AI Fundamentals
Artificial Intelligence (AI)
Machine Learning (ML)
Deep Learning (DL)
Supervised Learning
Unsupervised Learning
Semi-Supervised Learning
Self-Supervised Learning
Reinforcement Learning
Training vs Inference
Model
Features & Labels
Dataset (Training, Validation, Test)
Overfitting & Underfitting
Bias-Variance Tradeoff
Cross-Validation
Hyperparameters vs Parameters
Epoch, Batch, Iteration
Learning Rate
Loss Function
Gradient Descent (SGD, Adam, AdamW)

### Batch 2 — Classical ML Algorithms
Linear Regression
Logistic Regression
Decision Tree
Random Forest
Gradient Boosting (XGBoost, LightGBM, CatBoost)
Support Vector Machine (SVM)
K-Nearest Neighbors (KNN)
K-Means Clustering
DBSCAN
Principal Component Analysis (PCA)
Dimensionality Reduction
Feature Engineering
Feature Scaling (Normalization, Standardization)
One-Hot Encoding / Label Encoding
Handling Missing Data
Imbalanced Datasets (SMOTE, Class Weights)
Confusion Matrix / Precision / Recall / F1
ROC Curve / AUC
Ensemble Methods (Bagging, Boosting, Stacking)

### Batch 3 — Neural Networks & Deep Learning
Neuron / Perceptron
Activation Functions (ReLU, Sigmoid, Tanh, GELU, SiLU)
Feedforward Neural Network
Backpropagation
Vanishing / Exploding Gradients
Weight Initialization (Xavier, He, Kaiming)
Batch Normalization
Layer Normalization
Dropout
Regularization (L1 / L2)
Convolutional Neural Network (CNN)
Pooling (Max Pool, Average Pool)
Recurrent Neural Network (RNN)
LSTM (Long Short-Term Memory)
GRU (Gated Recurrent Unit)
Sequence-to-Sequence (Seq2Seq)
Autoencoder
Variational Autoencoder (VAE)
Generative Adversarial Network (GAN)
Skip Connections / Residual Networks (ResNet)

### Batch 4 — Transformers & Attention
Attention Mechanism
Self-Attention
Multi-Head Attention
Transformer Architecture
Positional Encoding / Positional Embeddings
Encoder-Decoder Architecture
BERT (Bidirectional Encoder Representations)
GPT (Generative Pre-trained Transformer)
T5 (Text-to-Text Transfer Transformer)
Tokenization (BPE, WordPiece, SentencePiece)
Embeddings (Word2Vec, GloVe, FastText)
Contextual Embeddings
Causal / Masked Language Modeling
Sequence Length / Context Window
KV Cache
Flash Attention
Mixture of Experts (MoE)
Scaling Laws (Chinchilla, Kaplan)

### Batch 5 — Large Language Models (LLMs)
LLM (Large Language Model)
Foundation Model
Pre-training vs Fine-tuning
Transfer Learning
Instruction Tuning
RLHF (Reinforcement Learning from Human Feedback)
DPO (Direct Preference Optimization)
Constitutional AI
System Prompt / User Prompt
Temperature / Top-k / Top-p (Nucleus Sampling)
Beam Search vs Greedy Decoding
Prompt Engineering
Few-Shot / Zero-Shot / One-Shot Learning
Chain-of-Thought (CoT) Prompting
Retrieval-Augmented Generation (RAG)
Hallucination
Guardrails / Safety Filters
Token Limits & Truncation
Structured Outputs (JSON Mode)
Function Calling / Tool Use

### Batch 6 — Fine-Tuning & Training
Full Fine-Tuning
LoRA (Low-Rank Adaptation)
QLoRA (Quantized LoRA)
PEFT (Parameter-Efficient Fine-Tuning)
Adapter Layers
Prefix Tuning / Prompt Tuning
Dataset Preparation for Fine-Tuning
Instruction Dataset Format (Alpaca, ShareGPT)
Training Frameworks (Hugging Face Trainer, Axolotl, LLaMA Factory)
Distributed Training (DDP, FSDP, DeepSpeed)
Mixed Precision Training (FP16, BF16)
Gradient Accumulation
Gradient Checkpointing
Model Parallelism vs Data Parallelism
Tensor Parallelism / Pipeline Parallelism
Training Loss Curves / Evaluation Metrics
BLEU / ROUGE / METEOR (NLP Metrics)
Perplexity

### Batch 7 — Inference & Optimization
Model Quantization (INT8, INT4, GPTQ, AWQ, GGUF)
Pruning
Knowledge Distillation
ONNX (Open Neural Network Exchange)
TensorRT
vLLM / TGI (Text Generation Inference)
Batched Inference
Speculative Decoding
Continuous Batching
Model Serving (Triton, BentoML, Ray Serve)
Latency vs Throughput
Tokens Per Second (TPS)
GPU Memory (VRAM) Estimation
CPU vs GPU vs TPU Inference
Edge Inference (ONNX Runtime, TFLite)
Model Caching / Warm Start
Streaming Responses

### Batch 8 — Computer Vision
Image Classification
Object Detection (YOLO, SSD, Faster R-CNN)
Semantic Segmentation
Instance Segmentation (Mask R-CNN)
Image Generation (Stable Diffusion, DALL·E, Midjourney)
Diffusion Models
Latent Space
U-Net
ControlNet
Image-to-Image / Inpainting / Outpainting
OCR (Optical Character Recognition)
Face Detection / Recognition
Pose Estimation
Data Augmentation (Flip, Rotate, CutOut, MixUp)
Transfer Learning (ImageNet Pretrained)
Vision Transformer (ViT)
CLIP (Contrastive Language-Image Pre-training)
Multimodal Models (GPT-4V, LLaVA, Gemini)

### Batch 9 — NLP & Text Processing
Natural Language Processing (NLP)
Text Preprocessing (Tokenization, Stemming, Lemmatization)
Stop Words
TF-IDF
Named Entity Recognition (NER)
Part-of-Speech Tagging
Sentiment Analysis
Text Classification
Text Summarization (Extractive vs Abstractive)
Machine Translation
Question Answering
Semantic Search / Vector Search
Text-to-Speech (TTS) / Speech-to-Text (STT)
Whisper (OpenAI)
Chatbot / Conversational AI
Document Parsing / Chunking for RAG

### Batch 10 — RAG & Vector Databases
RAG Architecture
Document Loading & Parsing
Text Chunking Strategies (Fixed, Recursive, Semantic)
Embedding Models (OpenAI Ada, BGE, E5, Cohere)
Vector Database (Pinecone, Weaviate, Qdrant, Chroma, Milvus, pgvector)
Similarity Search (Cosine, Euclidean, Dot Product)
HNSW Index
Hybrid Search (Vector + Keyword)
Re-Ranking (Cross-Encoder, Cohere Rerank)
Metadata Filtering
Contextual Retrieval
Parent-Child Chunking
Multi-Vector Retrieval
Knowledge Graphs + RAG
Evaluation (Faithfulness, Relevance, Context Recall)
LangChain / LlamaIndex / Haystack

### Batch 11 — AI Agents & Orchestration
AI Agent
Agent Loop (Observe → Think → Act)
Tool Use / Function Calling
Planning (ReAct, Plan-and-Execute)
Memory (Short-term, Long-term, Episodic)
Multi-Agent Systems
Agent Frameworks (LangGraph, CrewAI, AutoGen, Semantic Kernel)
Agentic RAG
Human-in-the-Loop
Guardrails for Agents
Task Decomposition
Code Interpreter / Sandbox Execution
Browser Agents
MCP (Model Context Protocol)
A2A (Agent-to-Agent Protocol)
Workflow Orchestration vs Autonomous Agents

### Batch 12 — MLOps & Production
MLOps Overview
Model Registry (MLflow, Weights & Biases)
Experiment Tracking
Data Versioning (DVC)
Feature Store
Model Versioning
CI/CD for ML Pipelines
A/B Testing for Models
Shadow Deployment / Champion-Challenger
Model Monitoring (Drift, Performance Degradation)
Data Drift vs Concept Drift
Model Explainability (SHAP, LIME)
Responsible AI / Bias & Fairness
GPU Cloud Providers (AWS, GCP, Azure, Lambda, RunPod)
Containerizing ML Models (Docker)
Kubernetes for ML (KubeFlow)
Cost Optimization (Spot Instances, Inference Caching)
Logging & Observability for AI

### Batch 13 — AI Ethics, Safety & Regulation
AI Alignment
AI Safety
Hallucination Mitigation
Prompt Injection / Jailbreaking
Red Teaming
Content Filtering / Moderation API
PII Detection & Redaction
Copyright & Training Data
Open Source vs Closed Source Models
GDPR & AI
EU AI Act
Deepfakes & Synthetic Media
Watermarking AI Content
Explainable AI (XAI)
Human Oversight

---

## PART 2 — Project Case Studies

### Case Study 1: RAG-Powered Knowledge Base Chatbot (DocuMind)

Build an internal knowledge base chatbot that:
- Ingests company documents (PDF, DOCX, Confluence pages)
- Chunks and embeds documents into a vector database
- Users ask natural language questions → retrieves relevant chunks → LLM generates answer with citations
- Supports multi-turn conversation with memory
- Includes admin panel: upload docs, view analytics, manage sources
- Deployed as a web app with streaming responses

**Cover in the case study:**
- Architecture diagram (ASCII): Ingestion pipeline + Query pipeline
- Tech stack: Python, FastAPI, LangChain/LlamaIndex, OpenAI/Ollama, Qdrant/pgvector, Next.js frontend
- Code snippets: document loader, chunking, embedding, retrieval chain, streaming API
- Evaluation strategy: faithfulness, relevance, hallucination rate
- Cost analysis: embedding costs, LLM token costs, vector DB hosting
- Production gotchas: chunk size tuning, metadata filtering, handling large docs
- Deployment pipeline: Docker + CI/CD → AWS/Azure
- Lessons learned

### Case Study 2: Real-Time Object Detection API (VisionGuard)

Build a real-time object detection service that:
- Accepts images/video streams via API
- Detects objects using YOLOv8 / YOLOv10
- Returns bounding boxes, labels, confidence scores
- Supports custom model fine-tuning (upload labeled data → retrain)
- Dashboard showing detection history, analytics, and alerts
- Optimized for edge deployment (ONNX Runtime)

**Cover in the case study:**
- Architecture diagram (ASCII): API → Model Inference → Post-processing → Response
- Tech stack: Python, FastAPI, Ultralytics YOLO, ONNX Runtime, Redis, React dashboard
- Code snippets: model loading, inference pipeline, fine-tuning script, API endpoint
- Custom training: labeling (Roboflow/CVAT), training config, evaluation (mAP, IoU)
- Optimization: INT8 quantization, batched inference, GPU vs CPU benchmarks
- Deployment: Docker, Triton Inference Server, Kubernetes
- Edge deployment: ONNX export, TFLite, Jetson Nano/Raspberry Pi
- Monitoring: inference latency, accuracy drift, model versioning
- Lessons learned
