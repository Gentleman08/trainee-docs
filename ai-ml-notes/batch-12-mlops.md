# Batch 12 — MLOps & Production
> How to ship, monitor, and maintain ML models in the real world — reliably and at scale.

---

## 1. MLOps Overview

### Definition
MLOps (Machine Learning Operations) is the practice of applying DevOps principles — automation, versioning, monitoring — to the full ML lifecycle: data → training → deployment → monitoring.

### Real-World Dev Example
A fraud-detection team uses MLOps to auto-retrain their model weekly on fresh transaction data, gate deployment behind accuracy thresholds, and alert on-call if recall drops below 90%.

```
Data → Train → Evaluate → [Pass?] → Deploy → Monitor
                              ↓ No
                           Retrain
```

### Gotchas & Dev Context
- MLOps ≠ just DevOps. Data drift and model decay are unique concerns.
- Start simple: even a cron job + logging beats nothing.
- Maturity levels: Level 0 (manual) → Level 1 (automated pipeline) → Level 2 (full CI/CD for ML).
- Tools ecosystem is fragmented — pick boring, proven tools first (MLflow, DVC, GitHub Actions).

### Production FAQ
**Q: When should I start caring about MLOps?**
A: The moment you have more than one model, more than one team member, or need reproducibility.

**Q: Is MLflow enough for a small team?**
A: Yes. MLflow (tracking + registry) + DVC (data versioning) + GitHub Actions covers 80% of MLOps needs for teams under 10.

---

## 2. Model Registry (MLflow, Weights & Biases)

### Definition
A model registry is a centralized catalog that stores trained model artifacts, their metadata, versions, and lifecycle stage (Staging → Production → Archived).

### Real-World Dev Example
After training 5 variants of a churn model, you push all to MLflow's registry. The best-performing one gets promoted to `Production`; others stay in `Staging` for comparison.

```
Experiment Runs
  ├── run_001 (acc=0.82) ──→ Registry: churn-model v1 [Archived]
  ├── run_002 (acc=0.87) ──→ Registry: churn-model v2 [Staging]
  └── run_003 (acc=0.91) ──→ Registry: churn-model v3 [Production] ✓
```

### Gotchas & Dev Context
- MLflow Registry is file/DB-backed and self-hostable; W&B is cloud-first with richer UI.
- Tag models with training data version — not just code version.
- `Staging` is not the same as "tested" — define your own promotion gates.
- W&B Artifacts track datasets too, not just models.

### Production FAQ
**Q: Can I roll back a model if production breaks?**
A: Yes — just promote the previous version back to `Production` in the registry and redeploy.

**Q: How do MLflow and W&B differ?**
A: MLflow is open-source and self-hosted; W&B is SaaS with better collaboration UX and richer visualizations but costs money at scale.

---

## 3. Experiment Tracking

### Definition
Experiment tracking is logging every training run's hyperparameters, metrics, artifacts, and environment so you can reproduce or compare results later.

### Real-World Dev Example
You run 30 LightGBM experiments with different `learning_rate` and `max_depth` combinations. MLflow logs each run; you filter by `val_auc > 0.88` and pick the best.

```python
import mlflow

mlflow.set_experiment("churn-lgbm")
with mlflow.start_run():
    mlflow.log_param("lr", 0.05)
    mlflow.log_param("depth", 6)
    mlflow.log_metric("val_auc", 0.91)
    mlflow.sklearn.log_model(model, "model")
```

### Gotchas & Dev Context
- Log *everything* — hardware, library versions, random seeds.
- Never rely on local `print()` logs for experiment comparison.
- Use `mlflow.autolog()` to capture sklearn/XGBoost/PyTorch params automatically.
- W&B `wandb.log()` streams metrics in real-time during training.

### Production FAQ
**Q: Do I need experiment tracking if I train only one model?**
A: You'll train more than one. Log from day one — retrofitting is painful.

**Q: How do I track experiments in notebooks?**
A: Use `mlflow.start_run()` in a cell or enable W&B with `wandb.init()`. Both work seamlessly in Jupyter.

---

## 4. Data Versioning (DVC)

### Definition
DVC (Data Version Control) versions large datasets and ML artifacts using Git-like semantics, while storing the actual files in remote storage (S3, GCS, Azure Blob).

### Real-World Dev Example
Your training CSV grows from 1M to 5M rows after a data refresh. DVC lets you `dvc add data/train.csv`, commit a `.dvc` pointer to Git, and push the raw file to S3 — keeping repos lean.

```
Git repo
  └── data/train.csv.dvc  ← tiny pointer file

S3 Bucket
  └── /dvc-cache/ab/3f...  ← actual 2GB CSV
```

### Gotchas & Dev Context
- `.dvc` files go in Git; actual data goes in remote storage. Never commit raw data to Git.
- `dvc repro` replays the entire pipeline from a `dvc.yaml` — like `make` for ML.
- Works with any remote: S3, GCS, Azure, SSH, local.
- Can version models too — treat them as DVC artifacts.

### Production FAQ
**Q: How do I share a dataset version with a teammate?**
A: Commit the `.dvc` file, push to S3 (`dvc push`), they run `dvc pull` to get the exact same file.

**Q: DVC vs Git LFS?**
A: DVC is ML-aware (pipelines, metrics, params); Git LFS just stores large files. Use DVC for ML projects.

---

## 5. Feature Store

### Definition
A feature store is a centralized system for storing, sharing, and serving engineered features — ensuring training and production use the *exact same* feature computation logic.

### Real-World Dev Example
Your model needs `user_30d_spend`. Without a feature store, the data science team computes it one way in training and the engineering team computes it differently in production → silent model failure. With Feast or Tecton, both sides share one definition.

```
Training Pipeline          Serving Pipeline
      │                          │
      └──── Feature Store ───────┘
           (one definition,
            consistent values)
```

### Gotchas & Dev Context
- The #1 benefit is eliminating **training-serving skew**.
- Offline store (for training): data warehouse / S3. Online store (for serving): Redis / DynamoDB.
- Popular tools: Feast (open-source), Tecton, Hopsworks, Vertex AI Feature Store.
- Overkill for small teams — start with shared utility functions first.

### Production FAQ
**Q: What's training-serving skew?**
A: When the features used to train differ from features computed at inference time, causing silent accuracy drops in production.

**Q: When do I need a feature store?**
A: When multiple models share the same features, or when real-time feature computation latency matters (e.g., recommendations, fraud).

---

## 6. Model Versioning

### Definition
Model versioning assigns unique, traceable identifiers to each trained model so you can reproduce, compare, audit, and roll back without confusion.

### Real-World Dev Example
`sentiment-model-v1` was trained on 2023 data. After fine-tuning on 2024 data, `v2` is deployed. A compliance audit asks "what data trained the model serving in Q1 2024?" — versioning answers this instantly.

```
v1 ── trained: Jan 2024, data: 2023.csv, f1: 0.84
v2 ── trained: Mar 2024, data: 2024.csv, f1: 0.89  ← Production
v3 ── trained: May 2024, data: 2024+synth.csv       ← Staging
```

### Gotchas & Dev Context
- Use semantic versioning semantics (major = architecture change, minor = retrain, patch = config tweak).
- Store the model *alongside* its training data version and code commit hash.
- MLflow Registry handles lifecycle; DVC handles artifact storage.
- Never overwrite a model in-place — always create a new version.

### Production FAQ
**Q: How is model versioning different from experiment tracking?**
A: Experiment tracking captures all runs; model versioning promotes *selected* artifacts into a governed registry with lifecycle stages.

**Q: Should I version model weights separately from code?**
A: Yes. Use Git for code, MLflow/DVC for model weights, and link them via run ID or commit hash in metadata.

---

## 7. CI/CD for ML Pipelines

### Definition
CI/CD for ML automates testing, validation, and deployment of models whenever code, data, or configuration changes — just like software CI/CD, but with data and model quality gates.

### Real-World Dev Example
A GitHub Actions workflow triggers on every PR: it runs unit tests, retrains on a sample, checks that new model accuracy ≥ baseline, and deploys to staging automatically if all checks pass.

```
PR opened
  → Lint & unit tests
  → Retrain (sample data)
  → Evaluate: acc >= baseline?
      ├── Yes → Deploy to Staging → Notify team
      └── No  → Block merge, post metrics comment
```

### Gotchas & Dev Context
- "Continuous Training" (CT) is separate from CI/CD — CT retrains on schedule or data trigger.
- Test your *data pipeline*, not just your model code.
- Tools: GitHub Actions, GitLab CI, Jenkins, Kubeflow Pipelines, Vertex AI Pipelines.
- Model quality gates prevent regressions — define thresholds before you start.

### Production FAQ
**Q: Should I retrain the full model on every PR?**
A: No — use a representative data sample for CI checks. Full retrains belong in scheduled CT pipelines.

**Q: What tests should an ML CI pipeline run?**
A: Data schema tests, training smoke tests, model performance regression tests, and inference latency benchmarks.

---

## 8. A/B Testing for Models

### Definition
A/B testing for models routes a portion of live traffic to a new model (B) while the current model (A) handles the rest, comparing real-world performance before full rollout.

### Real-World Dev Example
Your recommendation model v2 claims +5% CTR in offline eval. You send 10% of traffic to v2, measure live CTR for a week, confirm the lift, then ramp to 100%.

```
User Traffic (100%)
  ├── 90% ──→ Model A (current)   CTR: 3.2%
  └── 10% ──→ Model B (new)       CTR: 3.7% ✓ → promote
```

### Gotchas & Dev Context
- Always calculate required sample size before starting (use a power analysis).
- Beware of novelty effect — users may click more just because something changed.
- Use business metrics (revenue, retention), not just ML metrics (accuracy).
- Ensure random assignment — user ID hashing is safer than session-based splits.

### Production FAQ
**Q: How long should an A/B test run?**
A: Long enough to reach statistical significance AND cover a full business cycle (e.g., weekday + weekend patterns). Typically 1–2 weeks minimum.

**Q: What if Model B performs worse mid-test?**
A: Define a stopping criterion upfront (e.g., if CTR drops >15% vs A, abort automatically).

---

## 9. Shadow Deployment / Champion-Challenger

### Definition
Shadow deployment runs a new model in parallel with the production model — receiving the same inputs but *not* serving its outputs to users — so you can compare behavior risk-free.

### Real-World Dev Example
Before deploying a new credit-scoring model, you shadow it for 2 weeks. Every loan application hits both models. You compare score distributions and flag cases where they disagree by >20 points — all with zero user impact.

```
Request ──┬──→ Champion (Production) ──→ User Response
          └──→ Challenger (Shadow)   ──→ Logs only (no user impact)
                                           ↓
                                     Offline comparison
```

### Gotchas & Dev Context
- Shadow mode doubles inference compute cost — plan accordingly.
- Champion-Challenger is shadow + gradual traffic shift (e.g., 5% → 20% → 100%).
- Ideal for high-stakes models (credit, medical, fraud) where A/B risk is too high.
- Log both model outputs with the same request ID for easy comparison.

### Production FAQ
**Q: What's the difference between shadow and canary deployment?**
A: Canary serves real users (small %). Shadow serves no users — outputs are discarded. Shadow is safer; canary validates real UX impact.

**Q: How do I decide when to promote the challenger?**
A: Define promotion criteria upfront: e.g., challenger ≥ champion on AUC, latency within 10%, and no anomalous output patterns.

---

## 10. Model Monitoring (Drift, Performance Degradation)

### Definition
Model monitoring continuously tracks a deployed model's predictions, inputs, and business metrics to catch when it stops performing as expected.

### Real-World Dev Example
Your NLP sentiment model was trained on 2022 tweets. By 2024, new slang ("delulu", "rizz") causes prediction confidence to drop. Monitoring flags this before customers complain.

```
Live Predictions
  → Distribution checks (input drift?)
  → Prediction drift (output distribution shift?)
  → Label feedback loop (ground truth accuracy?)
  → Business KPI impact (revenue/conversion drop?)
```

### Gotchas & Dev Context
- Ground truth labels are often delayed (e.g., loan defaults take months) — use proxy metrics.
- Set *statistical* thresholds, not just heuristic ones (PSI, KS-test, Jensen-Shannon divergence).
- Tools: Evidently AI, WhyLabs, Arize, Fiddler, NannyML.
- Alert fatigue is real — start with fewer, high-confidence alerts.

### Production FAQ
**Q: How often should I run monitoring checks?**
A: Depends on data volume. High-traffic models: hourly. Lower volume: daily. Use statistical significance to determine window size.

**Q: What's the first thing to monitor after deployment?**
A: Input feature distributions — if features drift, everything downstream will too.

---

## 11. Data Drift vs Concept Drift

### Definition
- **Data Drift**: The *input* distribution changes (e.g., users now older on average).
- **Concept Drift**: The *relationship* between inputs and the target changes (e.g., "low income" used to predict default; new economic conditions change that).

### Real-World Dev Example
A loan default model trained pre-COVID: **data drift** = income distributions shifted. **Concept drift** = income-to-default relationship itself changed (stimulus payments altered repayment behavior).

```
Data Drift:      P(X) changes        → inputs look different
Concept Drift:   P(Y|X) changes      → same inputs, different correct outputs
```

### Gotchas & Dev Context
- Data drift is easier to detect (compare feature distributions); concept drift is harder (needs ground truth labels).
- Both require retraining — but concept drift is more urgent.
- Types of concept drift: sudden, gradual, seasonal, recurring.
- NannyML detects concept drift *without* labels using confidence-based methods.

### Production FAQ
**Q: Can a model suffer both simultaneously?**
A: Yes, and that's the worst case. Post-COVID models often faced both — shifted input distributions AND invalidated learned relationships.

**Q: How do I distinguish them in practice?**
A: Monitor feature distributions separately from model accuracy. Drift in features without accuracy drop = data drift. Accuracy drops without feature drift = concept drift.

---

## 12. Model Explainability (SHAP, LIME)

### Definition
Model explainability techniques reveal *why* a model made a specific prediction — which features drove the output and by how much.

### Real-World Dev Example
A bank's loan rejection model uses SHAP. When a customer appeals, the officer can say: "Your application was rejected primarily due to high debt-to-income ratio (−0.42) and short credit history (−0.28)."

```python
import shap
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)
shap.summary_plot(shap_values, X_test)
```

```
Feature Importance (SHAP):
debt_ratio    ████████████  -0.42
credit_age    ██████        -0.28
income        ███           +0.15
```

### Gotchas & Dev Context
- **SHAP**: Theoretically grounded (game theory), slower, exact for tree models.
- **LIME**: Faster, model-agnostic, locally approximate — less stable across runs.
- Global explanations ≠ local (per-prediction) explanations. Use both.
- Required by EU AI Act and some financial regulations.

### Production FAQ
**Q: Should I use SHAP or LIME?**
A: SHAP for tree models (fast, exact). LIME for black-box APIs or neural nets where SHAP is expensive.

**Q: Can explainability methods be wrong?**
A: Yes — LIME is an approximation and can be misleading for complex decision boundaries. Always validate against domain knowledge.

---

## 13. Responsible AI / Bias & Fairness

### Definition
Responsible AI ensures ML systems are fair, transparent, accountable, and don't systematically disadvantage groups based on protected attributes (race, gender, age, etc.).

### Real-World Dev Example
A resume screening model trained on historical hiring data learns to penalize resumes from women's colleges (because historical hires were mostly male). Fairness auditing catches this before deployment.

### Gotchas & Dev Context
- **Demographic parity**: Equal positive prediction rates across groups.
- **Equal opportunity**: Equal true positive rates across groups.
- These metrics can conflict — you can't always satisfy all simultaneously (Impossibility Theorem).
- Bias enters at data collection, labeling, feature engineering, and optimization — not just model choice.
- Tools: Fairlearn, IBM AI Fairness 360, Google's What-If Tool.
- Fairness is a sociotechnical problem, not purely a math problem.

### Production FAQ
**Q: How do I detect bias in my model?**
A: Slice your evaluation metrics by protected attributes (gender, age group, geography) and look for significant disparities.

**Q: If I remove protected attributes, is my model unbiased?**
A: No — proxy variables (zip code, name patterns, browsing behavior) can encode protected attributes. Removal alone is not sufficient.

---

## 14. GPU Cloud Providers (AWS, GCP, Azure, Lambda, RunPod)

### Definition
GPU cloud providers rent on-demand access to NVIDIA (and AMD) GPUs for training and inference — eliminating the need to own expensive hardware.

### Real-World Dev Example
Fine-tuning Llama 3 on your proprietary dataset requires 4× A100s for 6 hours. You spin up a Lambda Labs instance at ~$10/hr, fine-tune, save the weights to S3, and terminate — total: ~$60.

| Provider | Strength | Best For |
|----------|----------|----------|
| AWS (p4d, p5) | Ecosystem, SageMaker | Enterprise, compliance |
| GCP (A3/TPU) | TPUs, Vertex AI | Google stack |
| Azure (NDv4) | OpenAI partnership | Azure-native teams |
| Lambda Labs | Cheap A100/H100 | Budget training |
| RunPod | Cheapest spot GPUs | Hobbyists, quick jobs |

### Gotchas & Dev Context
- Spot/preemptible instances are 60–80% cheaper but can be interrupted — checkpoint frequently.
- Egress costs are often hidden — downloading 100GB of model weights from S3 costs money.
- Lambda and RunPod have less ecosystem tooling than AWS/GCP — more manual setup.

### Production FAQ
**Q: Which provider is cheapest for fine-tuning a 7B model?**
A: RunPod and Lambda Labs are typically cheapest for raw GPU time. AWS/GCP win if you're already in their ecosystem.

**Q: Should I use spot instances for training?**
A: Yes, if your training code checkpoints regularly (every 10–30 min). Use them for everything except final production serving.

---

## 15. Containerizing ML Models (Docker)

### Definition
Containerizing an ML model packages the model, its runtime, libraries, and dependencies into a Docker image — making it run identically everywhere: local, staging, production.

### Real-World Dev Example
Your model needs Python 3.10, PyTorch 2.1, and CUDA 12.1. Instead of "works on my machine," you build one Docker image and deploy it to any cloud in minutes.

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY model/ ./model/
COPY app.py .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Gotchas & Dev Context
- Use multi-stage builds to keep image sizes small — don't include training-time deps in serving images.
- GPU containers need NVIDIA Container Toolkit — `FROM nvidia/cuda:12.1-runtime-ubuntu22.04`.
- Pin *all* library versions in `requirements.txt` — floating versions break reproducibility.
- Use `.dockerignore` to exclude `__pycache__`, datasets, notebooks from the image.

### Production FAQ
**Q: How do I serve a model inside Docker?**
A: Wrap it with FastAPI or Flask, expose a `/predict` endpoint, and run `uvicorn` or `gunicorn` as the CMD.

**Q: My Docker image is 8GB — what do I do?**
A: Use a slim base image, multi-stage build to exclude build tools, and store model weights in S3 (download at container startup) rather than baking them in.

---

## 16. Kubernetes for ML (KubeFlow)

### Definition
Kubernetes (K8s) orchestrates containerized ML workloads at scale; KubeFlow is a Kubernetes-native ML platform that adds pipelines, notebooks, training operators, and model serving on top.

### Real-World Dev Example
You have 50 concurrent model training jobs and 10 serving endpoints. KubeFlow schedules GPU pods, auto-scales serving based on traffic, and retries failed training jobs — all declaratively via YAML.

```
KubeFlow Stack
  ├── Kubeflow Pipelines   ← DAG-based training workflows
  ├── Katib               ← Hyperparameter tuning (AutoML)
  ├── Training Operators  ← PyTorchJob, TFJob, MPIJob
  └── KServe              ← Model serving at scale
```

### Gotchas & Dev Context
- K8s has a steep learning curve — don't adopt it until you need multi-model, multi-team scale.
- KServe replaces KFServing (deprecated) — use KServe for new setups.
- GPU resource requests must be explicit: `resources: limits: nvidia.com/gpu: 1`.
- Managed KubeFlow: Vertex AI Pipelines (GCP), Amazon SageMaker Pipelines (AWS).

### Production FAQ
**Q: Do I need Kubernetes for a single model API?**
A: No. A single Docker container on a VM or cloud run service is simpler. Use K8s when you have many services, high traffic, or complex training pipelines.

**Q: What's the simplest KubeFlow entry point?**
A: KubeFlow Pipelines — start by converting your training script into a pipeline DAG. It's the most immediately useful component.

---

## 17. Cost Optimization (Spot Instances, Inference Caching)

### Definition
ML cost optimization reduces cloud spend by using cheaper compute (spot instances), avoiding redundant computation (caching), and right-sizing infrastructure.

### Real-World Dev Example
An LLM API serving 1M requests/day: 40% of prompts are near-identical FAQ queries. Caching those responses (Redis + semantic similarity) cuts LLM calls by 40%, saving ~$8,000/month.

```
Request → Cache lookup → Hit?  ──Yes──→ Return cached response (free)
                           │
                           No
                           ↓
                     LLM inference ($$) → Cache result → Return
```

### Gotchas & Dev Context
- **Spot instances**: 60–80% cheaper, but can be reclaimed in 2 min (AWS) or 30 sec (GCP). Use for training, not serving.
- **Inference caching**: Works best for LLMs and embedding models with repetitive inputs.
- **Quantization**: INT8/INT4 models run 2–4× faster and cheaper than FP32 — minimal accuracy loss.
- **Batch inference**: Group requests instead of one-at-a-time when latency allows.
- **Right-sizing**: Profile actual GPU/CPU usage — many pods run at 10% utilization.

### Production FAQ
**Q: How do I cache LLM responses safely?**
A: Exact-match cache for identical prompts; semantic cache (e.g., GPTCache) for similar prompts above a cosine similarity threshold (~0.95).

**Q: What's the biggest cost lever for LLM inference?**
A: Model size + context length. Use the smallest model that meets quality requirements, and truncate unnecessary context aggressively.

---

## 18. Logging & Observability for AI

### Definition
Observability for AI means capturing logs, metrics, and traces from your ML system so you can understand what's happening inside it, debug failures, and audit decisions.

### Real-World Dev Example
Your recommendation API starts returning a single item for 30% of users. Structured logs with `user_id`, `model_version`, `input_features`, and `output_scores` let you trace it to a feature pipeline bug that zero-filled one column.

```
Request In → [Log: input features]
           → Model Inference
           → [Log: output scores, latency, model version]
           → Response Out
           
Aggregate → Dashboards (Grafana)
          → Alerts (PagerDuty)
          → Traces (Jaeger / OpenTelemetry)
```

### Gotchas & Dev Context
- Log *model inputs and outputs* (with sampling for high-traffic systems) — you'll need them for debugging and drift detection.
- Use structured logging (JSON) — not plain text. Makes querying in CloudWatch/ELK trivial.
- Track latency percentiles (P50, P95, P99) — averages hide tail latency problems.
- OpenTelemetry is the emerging standard for traces — adopt it early.
- PII in logs is a compliance risk — hash or redact sensitive fields.

### Production FAQ
**Q: What's the difference between monitoring and observability?**
A: Monitoring tells you *when* something is wrong (alerts on known metrics). Observability lets you figure out *why* — even for unknown failure modes — via rich logs and traces.

**Q: How much logging is too much?**
A: Sample inputs/outputs at 1–10% for high-traffic systems. Log 100% of errors and anomalies. Balance cost vs. debuggability — but always log enough to reproduce incidents.

---

*End of Batch 12 — MLOps & Production*
