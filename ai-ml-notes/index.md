# AI & Machine Learning — Complete Developer Notes

> Beginner-friendly, production-aware notes covering everything from fundamentals to agents.  
> Each term includes a definition, real-world example, ASCII diagram (where helpful), gotchas, and a production FAQ.

---

## 📖 How to Use These Notes

1. **New to AI/ML?** Start with Batch 1 → Batch 2 → Batch 3 in order.
2. **Building with LLMs?** Jump to Batch 4 → Batch 5 → Batch 10 → Batch 11.
3. **Going to production?** Focus on Batch 7, Batch 12, and the Case Studies.
4. **Fine-tuning a model?** Batch 6 is your guide.
5. **Concerned about safety?** Read Batch 13 before deploying anything.

---

## 📚 Glossary Batches

| Batch | Topic | Terms |
|-------|-------|-------|
| [Batch 1](./batch-01-ai-fundamentals.md) | AI Fundamentals | AI, ML, DL, Supervised/Unsupervised Learning, Training vs Inference, Loss Function, Gradient Descent, and more |
| [Batch 2](./batch-02-classical-ml.md) | Classical ML Algorithms | Linear/Logistic Regression, Decision Tree, Random Forest, XGBoost, SVM, KNN, K-Means, PCA, Confusion Matrix, ROC/AUC, and more |
| [Batch 3](./batch-03-neural-networks.md) | Neural Networks & Deep Learning | Neurons, Activation Functions, CNN, RNN, LSTM, GRU, GAN, VAE, ResNet, Backpropagation, and more |
| [Batch 4](./batch-04-transformers-attention.md) | Transformers & Attention | Attention, Self-Attention, Multi-Head Attention, Transformer Architecture, BERT, GPT, T5, KV Cache, Flash Attention, MoE, Scaling Laws |
| [Batch 5](./batch-05-llms.md) | Large Language Models (LLMs) | LLM, Foundation Models, RLHF, DPO, Prompt Engineering, RAG, Hallucination, Function Calling, Structured Outputs |
| [Batch 6](./batch-06-fine-tuning.md) | Fine-Tuning & Training | LoRA, QLoRA, PEFT, Axolotl, DeepSpeed, Mixed Precision, Gradient Accumulation, BLEU/ROUGE, Perplexity |
| [Batch 7](./batch-07-inference-optimization.md) | Inference & Optimization | Quantization (GPTQ, AWQ, GGUF), Pruning, Knowledge Distillation, vLLM, TGI, Speculative Decoding, Edge Inference |
| [Batch 8](./batch-08-computer-vision.md) | Computer Vision | YOLO, Semantic Segmentation, Diffusion Models, Stable Diffusion, ControlNet, CLIP, ViT, Multimodal Models |
| [Batch 9](./batch-09-nlp.md) | NLP & Text Processing | Tokenization, TF-IDF, NER, Sentiment Analysis, Text Summarization, Whisper, Chatbots, Chunking for RAG |
| [Batch 10](./batch-10-rag-vector-db.md) | RAG & Vector Databases | RAG Architecture, Chunking Strategies, Embedding Models, Vector DBs (Pinecone, Qdrant), HNSW, Hybrid Search, Re-Ranking |
| [Batch 11](./batch-11-ai-agents.md) | AI Agents & Orchestration | Agent Loop, Tool Use, ReAct Planning, Multi-Agent Systems, LangGraph, CrewAI, MCP, A2A Protocol |
| [Batch 12](./batch-12-mlops.md) | MLOps & Production | MLflow, DVC, Feature Store, CI/CD for ML, A/B Testing, Model Monitoring, SHAP, Docker, KubeFlow, Cost Optimization |
| [Batch 13](./batch-13-ai-ethics-safety.md) | AI Ethics, Safety & Regulation | AI Alignment, Hallucination Mitigation, Prompt Injection, Red Teaming, PII Redaction, EU AI Act, XAI, Human Oversight |

---

## 🏗️ Project Case Studies

| Case Study | Description |
|------------|-------------|
| [Case Study 1 — DocuMind](./case-study-01-documind-rag-chatbot.md) | RAG-powered knowledge base chatbot: PDF/DOCX ingestion → Qdrant → LLM streaming answers with citations. Covers full architecture, code, deployment, cost analysis, and lessons learned. |
| [Case Study 2 — VisionGuard](./case-study-02-visionguard-object-detection.md) | Real-time object detection API: YOLOv8 → ONNX → Triton Inference Server → Kubernetes + edge deployment. Covers custom fine-tuning, INT8 quantization, benchmarks, and monitoring. |

---

## 🗺️ Learning Paths

### Path A — LLM Application Developer
```
Batch 1 → Batch 4 → Batch 5 → Batch 10 → Batch 11 → Case Study 1
```

### Path B — ML Engineer / Data Scientist
```
Batch 1 → Batch 2 → Batch 3 → Batch 6 → Batch 7 → Batch 12
```

### Path C — Computer Vision Engineer
```
Batch 1 → Batch 3 → Batch 8 → Batch 7 → Case Study 2
```

### Path D — AI Safety / Ethics Researcher
```
Batch 1 → Batch 5 → Batch 13 → Batch 11 → Batch 12
```

---

## 📂 File Structure

```
ai-ml-notes/
├── index.md                                    ← You are here
├── batch-tracker.md                            ← Batch completion status
├── batch-01-ai-fundamentals.md
├── batch-02-classical-ml.md
├── batch-03-neural-networks.md
├── batch-04-transformers-attention.md
├── batch-05-llms.md
├── batch-06-fine-tuning.md
├── batch-07-inference-optimization.md
├── batch-08-computer-vision.md
├── batch-09-nlp.md
├── batch-10-rag-vector-db.md
├── batch-11-ai-agents.md
├── batch-12-mlops.md
├── batch-13-ai-ethics-safety.md
├── case-study-01-documind-rag-chatbot.md
└── case-study-02-visionguard-object-detection.md
```

---

*Generated: May 2026 | Maintained for trainee developer education*
