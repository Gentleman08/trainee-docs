# 09 — Data Science, Machine Learning & AI (Examples 95–103)

[⬅️ Back to Handbook Index](README.md) · [⬅️ Previous: DevOps Tooling](08-devops-tooling.md)

---

## 🧾 What's special about ML images? (for non-developers)

- **Data scientists** write Python (sometimes R) using libraries like **pandas** (tables),
  **scikit-learn** (classic ML), **PyTorch** / **TensorFlow** (deep learning).
- A **model** is a file (often 100 MB–100 GB) produced by "training". **Inference** /
  **serving** = loading that model and using it to answer requests ("is this email spam?").
- **GPUs** (NVIDIA graphics cards) make deep learning 10–100× faster. They need the
  **CUDA** software stack.

### The 3 big problems with ML images

| Problem | Why | Mitigation |
|---------|-----|-----------|
| **Huge images** (5–15 GB) | PyTorch with CUDA alone is ~2.5 GB; models add more | CPU-only wheels when no GPU; keep models **out** of the image when large |
| **GPU plumbing** | Container needs access to the host's GPU + driver | NVIDIA Container Toolkit on the host; `--gpus all`; K8s device plugin |
| **Reproducibility** | Many numeric libraries, tied to specific CUDA versions | Pin everything; use lock files; match CUDA ↔ driver versions |

### GPU containers — how it fits together

```
 ┌────────────── Container ──────────────┐
 │ your code → PyTorch → CUDA runtime libs│   ← comes from the IMAGE
 └───────────────────┬───────────────────┘
                     │ (NVIDIA Container Toolkit injects the driver libs)
 ┌───────────────────▼───────────────────┐
 │ Host: NVIDIA DRIVER  +  GPU hardware   │   ← installed on the HOST, never in the image
 └───────────────────────────────────────┘
```

> ⚠️ **GPU gotcha:** The **host driver must be new enough** for the image's CUDA version
> (e.g. CUDA 12.4 needs driver ≥ 550-ish). Old driver → `CUDA driver version is insufficient
> for CUDA runtime version`. Check `nvidia-smi` on the host — top-right shows the max CUDA
> version the driver supports.

---

## Table of Contents

| # | Example | Key idea |
|---|---------|----------|
| 95 | [Jupyter notebook server](#example-95--jupyter-notebook-server) | Data-science workspace |
| 96 | [ML model API (CPU-only PyTorch)](#example-96--ml-model-api-cpu-only-pytorch) | Avoid 2 GB of unused CUDA |
| 97 | [GPU inference with CUDA](#example-97--gpu-inference-with-cuda) | NVIDIA base images |
| 98 | [TensorFlow Serving](#example-98--tensorflow-serving) | Purpose-built model server |
| 99 | [Hugging Face model: bake in vs download at runtime](#example-99--hugging-face-model-bake-in-vs-runtime) | Where models should live |
| 100 | [Ollama with a pre-pulled LLM](#example-100--ollama-with-a-pre-pulled-llm) | Local LLM serving |
| 101 | [PySpark batch job](#example-101--pyspark-batch-job) | Big data processing |
| 102 | [Apache Airflow custom image](#example-102--apache-airflow-custom-image) | Data pipeline orchestrator |
| 103 | [R Shiny dashboard](#example-103--r-shiny-dashboard) | R language web app |

---

## Example 95 — Jupyter notebook server

**🧾 What is this?** **Jupyter** is a browser-based "notebook" where data scientists mix
code, charts and notes. The **Jupyter Docker Stacks** project provides ready images.

```dockerfile
# Pick a dated tag from quay.io/jupyter/scipy-notebook for reproducibility
FROM quay.io/jupyter/scipy-notebook:2024-10-07

# Extra packages for this team (pinned)
COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
 && rm /tmp/requirements.txt \
 && fix-permissions "${CONDA_DIR}" \
 && fix-permissions "/home/${NB_USER}"

# System packages need root briefly
USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends graphviz \
 && rm -rf /var/lib/apt/lists/*
USER ${NB_UID}

WORKDIR /home/${NB_USER}/work
EXPOSE 8888
```

**🔍 Explained:**

- `scipy-notebook` — Jupyter + pandas, numpy, matplotlib, scikit-learn preinstalled.
  Variants: `pytorch-notebook`, `tensorflow-notebook`, `datascience-notebook` (Python+R+Julia).
- `NB_USER` / `NB_UID` / `NB_GID` — env vars from the base image: user `jovyan`, UID 1000.
- `fix-permissions` — helper script in the image that keeps folders writable for the user.

**⚠️ DevOps Gotchas:**

- Jupyter = **remote code execution by design**. Never expose it to the internet without
  authentication (token/password, or JupyterHub with SSO).
- Notebooks saved inside the container vanish — mount `/home/jovyan/work` as a volume.
- For teams, use **JupyterHub** (multi-user, on Kubernetes) rather than one shared container.

---

## Example 96 — ML model API (CPU-only PyTorch)

**🧾 What is this?** A FastAPI service that loads a PyTorch model and serves predictions.
Running on normal CPU servers, so we install the **CPU-only** PyTorch build — saving ~2 GB.

`requirements.txt`:

```text
fastapi==0.115.4
uvicorn[standard]==0.32.0
numpy==2.1.3
```

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm AS build
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" PIP_NO_CACHE_DIR=1
# CPU-only wheel index → no CUDA libraries downloaded
RUN pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.12-slim-bookworm
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=2 \
    MODEL_PATH=/models/model.pt
RUN useradd --system --uid 1001 --no-create-home app
WORKDIR /app
COPY --from=build /opt/venv /opt/venv
COPY --chown=1001:1001 app ./app
# Small model (<200 MB) shipped with the image; larger ones → see Example 99
COPY --chown=1001:1001 models/model.pt /models/model.pt
USER 1001
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
```

**🔍 Explained:**

- `--index-url https://download.pytorch.org/whl/cpu` — PyTorch hosts separate wheel sets;
  the default from PyPI on Linux includes CUDA (~2.5 GB). CPU wheel is ~200 MB.
- `OMP_NUM_THREADS=2` — limits math-library threads. Otherwise PyTorch sees the **host's**
  64 cores inside a 2-CPU container and thrashes.
- `--workers 1` — each worker loads its own copy of the model into memory. Scale with
  replicas, not workers, unless memory is plentiful.

**⚠️ DevOps Gotchas:**

- Model loading can take 10–60 s → set Kubernetes **startup/readiness probes** with
  enough delay, or traffic hits a pod that isn't ready.
- Memory: model size × workers + overhead. Under-sized limits → OOMKilled during load.

---

## Example 97 — GPU inference with CUDA

**🧾 What is this?** Same idea, on a **GPU** node. We start from NVIDIA's CUDA image.

```dockerfile
# syntax=docker/dockerfile:1
# "runtime" variant: CUDA + cuDNN runtime libraries (no compilers). "devel" adds nvcc (for building).
FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-pip python3-venv \
 && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# PyTorch wheels built for CUDA 12.4
RUN pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cu124
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN useradd --system --uid 1001 --no-create-home app
WORKDIR /app
COPY --chown=1001:1001 app ./app
USER 1001
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**▶️ Run:**

```bash
# Host needs the NVIDIA driver + NVIDIA Container Toolkit
docker run --gpus all -p 8000:8000 gpu-api:1.0.0
# Quick check that the container sees the GPU:
docker run --rm --gpus all gpu-api:1.0.0 python -c "import torch; print(torch.cuda.is_available())"
```

**🔍 Explained:**

- `nvidia/cuda:<cuda>-cudnn-runtime-<os>` — tag tells you CUDA version, cuDNN included,
  runtime (not devel), OS.
- `whl/cu124` — PyTorch build matching CUDA 12.4.
- `--gpus all` — exposes host GPUs to the container (requires NVIDIA Container Toolkit).

**⚠️ DevOps Gotchas:**

- In Kubernetes: install the **NVIDIA device plugin** (or GPU Operator), then request GPUs
  with `resources.limits: nvidia.com/gpu: 1`. Without the limit, the pod lands on a GPU node
  but can't see the GPU.
- PyTorch pip wheels already bundle most CUDA libs, so a plain `python:3.12-slim` base often
  works too. Use the `nvidia/cuda` base when other tools need system CUDA libraries.
- GPU nodes are expensive — use taints/tolerations so normal pods don't occupy them.

---

## Example 98 — TensorFlow Serving

**🧾 What is this?** **TensorFlow Serving** is Google's high-performance server for
TensorFlow models. No Python code needed — just put the exported "SavedModel" folder in the
right place.

```
models/
└── fraud_model/
    └── 1/                 ← version number (folder name MUST be an integer)
        ├── saved_model.pb
        └── variables/
```

```dockerfile
FROM tensorflow/serving:2.17.0
# Models live at /models/<MODEL_NAME>/<version>/
COPY models/fraud_model /models/fraud_model
ENV MODEL_NAME=fraud_model
# 8500 = gRPC API, 8501 = REST API
EXPOSE 8500 8501
```

**▶️ Test:**

```bash
docker run -p 8501:8501 fraud-serving:1
curl -X POST http://localhost:8501/v1/models/fraud_model:predict \
  -d '{"instances": [[0.1, 0.5, 3.2, 1.0]]}'
```

**🔍 Explained:**

- `MODEL_NAME` — the base image's entrypoint serves `/models/${MODEL_NAME}` automatically.
- Version folders allow side-by-side versions; by default the **highest** number is served.
- GPU variant: `tensorflow/serving:2.17.0-gpu`.

**⚠️ DevOps Gotchas:**

- A model folder named `v1` instead of `1` → "No versions of servable found". Must be numeric.
- Multi-model serving uses a `--model_config_file` instead of `MODEL_NAME`.
- Other model servers using the same idea: **NVIDIA Triton**, **TorchServe**, **KServe**.

---

## Example 99 — Hugging Face model: bake in vs runtime

**🧾 What is this?** **Hugging Face** hosts thousands of pre-trained models. Where should
the model files live: **inside the image** or **downloaded at startup**?

| | Bake into image | Download at runtime / mount volume |
|---|----------------|-----------------------------------|
| Startup | ✅ Fast, no network needed | ❌ Slow first start; needs internet/HF access |
| Image size | ❌ Huge (GBs) → slow pulls, registry costs | ✅ Small image |
| Reproducibility | ✅ Exact model version locked in image | ⚠️ Must pin model revision |
| Good for | Small models (< ~1–2 GB), air-gapped clusters | Large models (LLMs), shared volume/cache |

**Option A — bake a small model in:**

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/opt/hf \
    HF_HUB_OFFLINE=0
RUN pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu \
 && pip install transformers==4.46.2 fastapi==0.115.4 "uvicorn[standard]==0.32.0"

# Download a PINNED model revision at build time into HF_HOME
ARG MODEL_ID=distilbert/distilbert-base-uncased-finetuned-sst-2-english
# Replace "main" with the exact commit hash from the model's "Files and versions" page on huggingface.co
ARG MODEL_REVISION=main
RUN python -c "from huggingface_hub import snapshot_download; \
snapshot_download(repo_id='${MODEL_ID}', revision='${MODEL_REVISION}')"

# From now on, never reach out to the internet
ENV HF_HUB_OFFLINE=1 \
    MODEL_ID=${MODEL_ID} \
    MODEL_REVISION=${MODEL_REVISION}

RUN useradd --system --uid 1001 --no-create-home app && chown -R 1001:1001 /opt/hf
WORKDIR /app
COPY --chown=1001:1001 app ./app
USER 1001
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Option B — download at runtime into a mounted cache (large models):** same Dockerfile
**without** the `snapshot_download` step and with `HF_HUB_OFFLINE=0`; then mount a
persistent volume at `/opt/hf` so the download happens once.

**🔍 Explained:**

- `HF_HOME` — where Hugging Face libraries store downloaded models.
- `revision=<commit hash>` — pins the exact model version (models get updated on the Hub!).
- `HF_HUB_OFFLINE=1` — at runtime, fail instead of silently downloading something new.
- Gated/private models need `HF_TOKEN` → pass as a **build secret** (Example 104), never `ARG`.

**⚠️ DevOps Gotchas:**

- `chown -R` on GBs of model files in a separate layer **duplicates them** (layer copy-on-write).
  Better: download as the target user, or use `COPY --chown` from a download stage.
- Multi-GB layers can hit registry upload timeouts and make node scale-up slow. Consider
  pre-pulling images on GPU nodes or streaming images (e.g. AKS Artifact Streaming).

---

## Example 100 — Ollama with a pre-pulled LLM

**🧾 What is this?** **Ollama** runs open-source LLMs (Llama, Mistral, Qwen…) locally with a
simple API. We bake a small model in so the container works offline immediately.

```dockerfile
FROM ollama/ollama:0.4.1

ARG MODEL=llama3.2:1b

# The server must be running to pull a model: start it in the background,
# wait until it answers, pull the model, then stop it — all in one RUN.
RUN ollama serve & SERVER_PID=$!; \
    for i in $(seq 1 30); do ollama list >/dev/null 2>&1 && break; sleep 1; done; \
    ollama pull "${MODEL}" && \
    kill "$SERVER_PID"

ENV OLLAMA_HOST=0.0.0.0:11434 \
    OLLAMA_KEEP_ALIVE=24h
EXPOSE 11434
# Base image ENTRYPOINT is "ollama" and CMD is "serve"
```

**▶️ Test:**

```bash
docker run -d -p 11434:11434 my-ollama
curl http://localhost:11434/api/generate -d '{"model":"llama3.2:1b","prompt":"Say hi","stream":false}'
```

**🔍 Explained:**

- `ollama serve &` — `&` runs the server in the background *during the build step*.
- The `for` loop polls up to 30 s until the server answers (more reliable than a fixed `sleep`).
- `SERVER_PID=$!` — `$!` is the process ID of the last background command; `kill "$SERVER_PID"`
  stops the server so the RUN step finishes.
- `OLLAMA_KEEP_ALIVE=24h` — keep the model loaded in memory between requests.

**⚠️ DevOps Gotchas:**

- Even "small" LLMs are GBs; 7–8B models need ~5 GB+ RAM/VRAM. Size nodes accordingly.
- For bigger/production LLM serving (batching, many users), teams use **vLLM** or
  **NVIDIA NIM / Triton** instead — but the image-size and GPU lessons are the same.
- The Ollama API has **no authentication**. Put it behind an authenticated gateway.

---

## Example 101 — PySpark batch job

**🧾 What is this?** **Apache Spark** processes huge datasets across many machines.
**PySpark** = Spark with Python. We package a Spark job for `spark-submit` (e.g. on Spark on
Kubernetes).

```dockerfile
FROM apache/spark:3.5.3-scala2.12-java17-python3-ubuntu

USER root
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Extra JARs (e.g. Azure Data Lake / S3 connectors) go into Spark's jars folder
ADD --chown=spark:spark --checksum=sha256:REPLACE_WITH_REAL_SHA256 \
    https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-azure/3.3.4/hadoop-azure-3.3.4.jar \
    /opt/spark/jars/

COPY --chown=spark:spark jobs/ /opt/spark/work-dir/jobs/

# The base image's spark user has UID 185
USER 185
WORKDIR /opt/spark/work-dir
```

**▶️ Run locally:**

```bash
docker run --rm spark-jobs:1.0 /opt/spark/bin/spark-submit --master local[2] jobs/daily_sales.py
```

**🔍 Explained:**

- `apache/spark:...-python3` — official image with Spark, Java, and Python.
- `ADD --checksum=sha256:... <URL>` — the **one good use of `ADD` with a URL**: BuildKit
  downloads it and **verifies the checksum** (replace the placeholder with the real hash).
- `USER 185` — the built-in `spark` user.

**⚠️ DevOps Gotchas:**

- **Python and library versions must match** between Spark driver and executors — use the
  **same image** for both.
- Connector JAR versions must match the **Hadoop version** bundled with Spark, or you get
  `NoSuchMethodError`. Version-matching is the #1 Spark packaging headache.

---

## Example 102 — Apache Airflow custom image

**🧾 What is this?** **Airflow** schedules and orchestrates data pipelines ("DAGs" — Python
files describing tasks and their order). The official guide recommends **extending** the
official image.

```dockerfile
FROM apache/airflow:2.10.3-python3.12

# OS packages (as root)
USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends libpq5 \
 && rm -rf /var/lib/apt/lists/*

# Python packages MUST be installed as the airflow user, pinned with Airflow's constraints
USER airflow
ARG AIRFLOW_VERSION=2.10.3
ARG PYTHON_VERSION=3.12
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir \
      "apache-airflow==${AIRFLOW_VERSION}" \
      -r /tmp/requirements.txt \
      --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

# DAGs and plugins baked in (alternative: git-sync sidecar)
COPY --chown=airflow:root dags/    /opt/airflow/dags/
COPY --chown=airflow:root plugins/ /opt/airflow/plugins/
```

**🔍 Explained:**

- `"apache-airflow==${AIRFLOW_VERSION}"` in the same pip command — prevents pip from
  accidentally upgrading/downgrading Airflow itself while installing your packages.
- `--constraint ...` — Airflow's tested set of dependency versions; avoids dependency hell.
- `--chown=airflow:root` — Airflow's images use GID 0 (root group) for OpenShift compatibility.

**⚠️ DevOps Gotchas:**

- Installing Python packages as **root** in this image breaks things (the docs explicitly
  warn). Always `USER airflow` for pip.
- The **same image** must be used by scheduler, webserver, workers and triggerer; a DAG using a
  package missing in the worker image fails only when that task runs.
- Baking DAGs = redeploy for every DAG change. Many teams use **git-sync** to pull DAGs live
  and keep the image for dependencies only.

---

## Example 103 — R Shiny dashboard

**🧾 What is this?** **R** is a statistics language popular with analysts. **Shiny** builds
interactive web dashboards in R. The **Rocker** project publishes trusted R images.

```dockerfile
FROM rocker/shiny:4.4.1

# install2.r (from littler) installs CRAN packages; --error fails the build if one fails
RUN install2.r --error --skipinstalled --ncpus -1 \
      dplyr ggplot2 DT plotly \
 && rm -rf /tmp/downloaded_packages

# Remove the sample apps, add ours
RUN rm -rf /srv/shiny-server/*
COPY --chown=shiny:shiny app/ /srv/shiny-server/

USER shiny
EXPOSE 3838
CMD ["/usr/bin/shiny-server"]
```

**🔍 Explained:**

- `rocker/shiny:4.4.1` — R 4.4.1 + Shiny Server. Rocker images are **version-pinned**: CRAN
  packages install from a dated snapshot matching that R version → reproducible.
- `--error` — without it, a failed package install only prints a warning and the build "succeeds".
- `--ncpus -1` — compile packages using all CPU cores (faster builds).
- Apps in `/srv/shiny-server/` are served at `http://host:3838/`.

**⚠️ DevOps Gotchas:**

- R packages often compile C/C++/Fortran code and need system libraries (`libxml2-dev`,
  `libcurl4-openssl-dev`, `libssl-dev`). Build errors like "xml2-config not found" mean a
  missing `-dev` package. Prebuilt binaries from **Posit Package Manager** avoid compiling.
- Like Streamlit, Shiny uses **WebSockets** → proxy and sticky-session configuration needed.

---

**Next:** [10 — Advanced Patterns & Production Hardening ➡️](10-advanced-patterns.md)
