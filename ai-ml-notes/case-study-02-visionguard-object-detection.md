# Case Study 2 — VisionGuard: Real-Time Object Detection API
> A production-grade object detection service built with YOLOv8, FastAPI, ONNX Runtime, and Triton Inference Server.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture Diagrams](#2-architecture-diagrams)
3. [Tech Stack](#3-tech-stack)
4. [Step-by-Step Build](#4-step-by-step-build)
5. [Code Snippets](#5-code-snippets)
6. [Custom Training Guide](#6-custom-training-guide)
7. [Optimization & Benchmarks](#7-optimization--benchmarks)
8. [Deployment](#8-deployment)
9. [Monitoring](#9-monitoring)
10. [Production Gotchas](#10-production-gotchas)
11. [Lessons Learned](#11-lessons-learned)

---

## 1. Project Overview

### What Is VisionGuard?

VisionGuard is a **real-time object detection API service** that ingests images and video streams, runs inference with YOLOv8 or YOLOv10, and returns structured JSON payloads containing bounding boxes, class labels, and confidence scores. Beyond out-of-the-box detection, VisionGuard includes a **custom fine-tuning pipeline** — customers can upload labeled image datasets, trigger a retraining job, and deploy their domain-specific model without writing a single line of code.

The service is fronted by a **FastAPI** application, backed by **ONNX Runtime** for CPU/edge and **NVIDIA Triton Inference Server** for GPU-accelerated cloud deployments. A companion dashboard provides real-time detection history, alert thresholds, and analytics charts.

### Who Uses It?

| Industry | Use Case | Key Metric |
|---|---|---|
| Retail | Shelf-out-of-stock detection, shrinkage / theft alerts | Latency < 200 ms per frame |
| Manufacturing | Surface defect detection on production lines | mAP@50 > 0.92 |
| Logistics | Package counting, label verification at conveyor belts | Throughput > 30 FPS |
| Smart Cities | Pedestrian / vehicle density monitoring | Edge deployment on Jetson Nano |
| Agriculture | Crop disease spotting from drone imagery | Custom dataset fine-tuning |

### Business Problem It Solves

Traditional rule-based computer vision (colour thresholding, template matching) breaks down the moment lighting conditions, product SKUs, or camera angles change. ML-based object detection generalises far better — but deploying it at scale requires solving:

- **Inference latency** — CCTV feeds demand near-real-time response.
- **Custom domain knowledge** — COCO-pretrained weights don't know what a "dented can lid" looks like.
- **Edge vs. cloud tradeoff** — privacy-sensitive sites need on-device inference; others can afford cloud GPUs.
- **Model lifecycle management** — models drift as products change; retraining must be low-friction.

VisionGuard wraps all of these concerns into a single opinionated platform.

---

## 2. Architecture Diagrams

### 2.1 API Inference Flow

```
Client (HTTP/RTSP)
        │
        │  POST /detect  (multipart image OR stream URL)
        ▼
┌───────────────────┐
│   FastAPI (uvicorn│
│   + gunicorn)     │
│                   │
│  ① Auth (JWT)     │
│  ② Rate-limit     │
│  ③ Input validate │
└────────┬──────────┘
         │
         │  Check Redis cache (image hash → cached result)
         ▼
┌────────────────────┐         Cache HIT
│   Redis 7.x        │ ─────────────────────────────────────►  JSON Response
│  (result cache)    │
└────────┬───────────┘
         │ Cache MISS
         ▼
┌────────────────────────────┐
│  Pre-processing Worker     │
│  ─ Decode image (PIL/cv2)  │
│  ─ Resize → letterbox      │
│  ─ Normalize [0,1]         │
│  ─ HWC → CHW tensor        │
└────────┬───────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│  Inference Backend (selected at startup) │
│                                          │
│  Option A: ONNX Runtime (CPU / CUDA EP)  │
│  Option B: Triton gRPC client            │
│  Option C: PyTorch (ultralytics)         │
└────────┬─────────────────────────────────┘
         │  Raw tensors  [B, num_preds, 85]
         ▼
┌──────────────────────────────┐
│  Post-processing             │
│  ─ NMS (IoU 0.45, conf 0.25) │
│  ─ Denormalize box coords    │
│  ─ Map class IDs → labels    │
│  ─ Apply alert thresholds    │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────┐
│  PostgreSQL + Redis  │  ← persist detection events
│  (history / alerts)  │
└────────┬─────────────┘
         │
         ▼
    JSON Response
    {
      "detections": [...],
      "inference_ms": 18.4,
      "model_version": "v2.1"
    }
```

### 2.2 Custom Fine-Tuning Pipeline

```
  Customer uploads labeled images
  (ZIP: images/ + labels/ YOLO format)
           │
           ▼
┌──────────────────────────┐
│  Upload API endpoint     │
│  ─ Validate label format │
│  ─ Store in S3 / MinIO   │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Roboflow Export         │
│  (or CVAT XML → convert) │
│  Generates data.yaml     │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│  Training Job (Celery worker / k8s Job)  │
│                                          │
│  yolo train                              │
│    model=yolov8n.pt                      │
│    data=data.yaml                        │
│    epochs=100  imgsz=640                 │
│    batch=16    device=0                  │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Evaluation              │
│  ─ mAP@50, mAP@50-95     │
│  ─ Precision / Recall    │
│  ─ Confusion matrix      │
│  ─ Compare vs. baseline  │
└────────┬─────────────────┘
         │  (Fails quality gate → notify, discard)
         │  (Passes → proceed)
         ▼
┌──────────────────────────┐
│  ONNX Export             │
│  ─ FP32 → FP16 → INT8    │
│  ─ Validate accuracy     │
│  ─ MLflow model registry │
└────────┬─────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Hot-swap to Triton / ONNX RT   │
│  Zero-downtime model update     │
└─────────────────────────────────┘
```

### 2.3 Deployment Architecture

```
Developer
   │  git push
   ▼
┌──────────────┐
│  GitHub      │
│  Actions CI  │
│  ─ Lint      │
│  ─ Test      │
│  ─ Build img │
└──────┬───────┘
       │  docker push → ECR / GHCR
       ▼
┌──────────────────────────────────────────────────────┐
│                   Kubernetes Cluster                  │
│                                                      │
│  ┌─────────────┐    ┌────────────────────────────┐  │
│  │   Ingress   │    │  Namespace: visionguard     │  │
│  │  (nginx)    │───►│                            │  │
│  └─────────────┘    │  ┌──────────────────────┐  │  │
│                     │  │  FastAPI Deployment  │  │  │
│                     │  │  (3 replicas)        │  │  │
│                     │  └──────────┬───────────┘  │  │
│                     │             │ gRPC          │  │
│                     │  ┌──────────▼───────────┐  │  │
│                     │  │  Triton Inference    │  │  │
│                     │  │  Server Deployment   │  │  │
│                     │  │  (GPU node pool)     │  │  │
│                     │  └──────────────────────┘  │  │
│                     │                            │  │
│                     │  ┌──────────────────────┐  │  │
│                     │  │  Redis StatefulSet   │  │  │
│                     │  └──────────────────────┘  │  │
│                     │                            │  │
│                     │  ┌──────────────────────┐  │  │
│                     │  │  PostgreSQL (RDS /   │  │  │
│                     │  │  CloudNativePG)      │  │  │
│                     │  └──────────────────────┘  │  │
│                     └────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
       │
       │  Edge path
       ▼
┌───────────────────────────┐
│  Jetson Nano / RPi 4      │
│  ONNX Runtime (TRT EP)    │
│  Lightweight FastAPI      │
│  Local Redis (optional)   │
└───────────────────────────┘
```

---

## 3. Tech Stack

| Layer | Technology | Version / Notes |
|---|---|---|
| **Object Detection** | Ultralytics YOLOv8 / YOLOv10 | `ultralytics==8.2.x` |
| **API Framework** | FastAPI + Uvicorn + Gunicorn | `fastapi==0.111.x` |
| **Inference (Cloud)** | NVIDIA Triton Inference Server | `nvcr.io/nvidia/tritonserver:24.04` |
| **Inference (Edge)** | ONNX Runtime | `onnxruntime-gpu==1.18.x` |
| **Quantization** | ONNX Runtime Quantization Tools | INT8 static / dynamic |
| **Async Task Queue** | Celery + Redis | `celery==5.3.x` |
| **Cache** | Redis 7.x | Result caching, job queues |
| **Database** | PostgreSQL 16 | Detection history, model registry metadata |
| **Object Storage** | MinIO (self-hosted) / AWS S3 | Training data, model artifacts |
| **Model Registry** | MLflow | `mlflow==2.13.x` |
| **Labeling** | Roboflow / CVAT | Dataset management |
| **Containerisation** | Docker 26.x | Multi-stage builds |
| **Orchestration** | Kubernetes (EKS / GKE) | `kubectl`, Helm |
| **Monitoring** | Prometheus + Grafana | Custom metrics endpoint |
| **Tracing** | OpenTelemetry + Jaeger | Distributed request tracing |
| **CI/CD** | GitHub Actions | Lint → Test → Build → Deploy |
| **Image Processing** | OpenCV 4.9.x, Pillow 10.x | Pre/post-processing |
| **Data Augmentation** | Albumentations 1.4.x | Training pipeline |
| **Language** | Python 3.11 | Throughout |

---

## 4. Step-by-Step Build

### Phase 1 — Environment Setup & YOLOv8 Baseline

**Goal:** Get a working local inference loop before touching any API code.

```bash
# Create isolated environment
python -m venv visionguard-env
source visionguard-env/bin/activate   # Windows: visionguard-env\Scripts\activate

# Core dependencies
pip install ultralytics==8.2.82 \
            onnxruntime-gpu==1.18.0 \
            fastapi==0.111.1 \
            uvicorn[standard]==0.30.1 \
            python-multipart==0.0.9 \
            redis==5.0.7 \
            celery==5.3.6 \
            sqlalchemy==2.0.31 \
            asyncpg==0.29.0 \
            mlflow==2.13.2 \
            prometheus-client==0.20.0 \
            pillow==10.4.0 \
            opencv-python-headless==4.9.0.80 \
            albumentations==1.4.10
```

Validate your GPU is visible:

```bash
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
# Expected: True  NVIDIA GeForce RTX 3090
```

### Phase 2 — Inference API

**Goal:** Wrap YOLOv8 inference in a production-ready FastAPI service with input validation, error handling, and result caching.

Project layout:
```
visionguard/
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI app factory
│   ├── routers/
│   │   ├── detect.py       # /detect endpoint
│   │   └── models.py       # /models (list/upload/activate)
│   ├── services/
│   │   ├── inference.py    # YOLO / ONNX RT abstraction
│   │   ├── cache.py        # Redis helpers
│   │   └── postprocess.py  # NMS, label mapping
│   ├── models/             # SQLAlchemy ORM models
│   ├── schemas/            # Pydantic request/response schemas
│   └── config.py           # Settings (pydantic-settings)
├── training/
│   ├── train.py
│   ├── export_onnx.py
│   └── quantize.py
├── triton_models/          # Triton model repository
├── k8s/                    # Kubernetes manifests
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

### Phase 3 — Custom Training Pipeline

**Goal:** Accept user-uploaded labeled datasets, launch a Celery training job, evaluate the result, and register the model in MLflow.

Key steps:
1. Upload handler validates YOLO label format (class_id cx cy w h, normalised).
2. `data.yaml` is auto-generated from the uploaded class list.
3. Celery task invokes `yolo train` with `subprocess` or the Python API.
4. After training, evaluation metrics are scraped from `results.csv`.
5. If `mAP@50 >= threshold`, export to ONNX and register in MLflow.
6. Hot-swap: Triton's model repository is updated atomically; the old version is kept for rollback.

### Phase 4 — Optimisation (ONNX, INT8)

**Goal:** Reduce inference latency and memory footprint for edge and high-throughput scenarios.

Steps:
1. Export trained PyTorch `.pt` model to ONNX (FP32).
2. Apply FP16 conversion using `onnxconverter-common`.
3. Apply INT8 static quantization using a calibration dataset (≈ 200 representative images).
4. Benchmark FP32 vs FP16 vs INT8 with `onnxruntime` and record latency/accuracy.
5. For Jetson: replace ONNX Runtime with TensorRT EP for further 2–3× speedup.

### Phase 5 — Dashboard

**Goal:** Give end-users visibility into detections, alerts, and system health.

Built with **Next.js 14** (TypeScript) + **Recharts** on the frontend. Backend serves `/api/history`, `/api/alerts`, and WebSocket push for live feeds.

Key dashboard features:
- Detection event table with thumbnail crops of detected objects.
- Time-series chart of detections per class per hour.
- Alert configuration (e.g., "notify if class=person AND confidence > 0.85 AND zone=entrance").
- Model management page: upload dataset → poll training status → activate model.
- Prometheus metrics surface directly to Grafana via the `/metrics` endpoint.

### Phase 6 — Deployment

**Goal:** Ship the service to Kubernetes with GPU node support, health checks, and zero-downtime rolling updates.

See [Section 8](#8-deployment) for full manifests and Dockerfile.

---

## 5. Code Snippets

### 5.1 — YOLOv8 Model Loading and Inference

```python
# app/services/inference.py
import time
import numpy as np
from pathlib import Path
from typing import Any

import cv2
from ultralytics import YOLO

# ── Singleton model holder (loaded once at startup) ──────────────────────────
_model: YOLO | None = None

def load_model(weights_path: str = "yolov8n.pt") -> YOLO:
    """Load YOLOv8 model into GPU memory (or CPU if no GPU available).

    Call this once inside the FastAPI `lifespan` context manager so the model
    is warm before the first request arrives.
    """
    global _model
    if _model is None:
        _model = YOLO(weights_path)
        # Force a dummy forward pass to JIT-compile any CUDA kernels
        dummy = np.zeros((640, 640, 3), dtype=np.uint8)
        _model.predict(dummy, verbose=False)
    return _model


def run_inference(
    image: np.ndarray,           # HWC, BGR, uint8
    conf_threshold: float = 0.25,
    iou_threshold: float = 0.45,
    max_detections: int = 300,
    classes: list[int] | None = None,  # Filter to specific class IDs
) -> dict[str, Any]:
    """Run YOLOv8 inference and return structured detections.

    Returns
    -------
    dict with keys:
        detections  : list of {box, label, class_id, confidence}
        inference_ms: wall-clock latency in milliseconds
        image_shape : (H, W) of the input image
    """
    model = load_model()

    t0 = time.perf_counter()
    results = model.predict(
        source=image,
        conf=conf_threshold,
        iou=iou_threshold,
        max_det=max_detections,
        classes=classes,
        verbose=False,       # Suppress console spam in production
        stream=False,
    )
    inference_ms = (time.perf_counter() - t0) * 1000

    detections = []
    for result in results:
        boxes = result.boxes
        for i in range(len(boxes)):
            x1, y1, x2, y2 = boxes.xyxy[i].tolist()
            detections.append({
                "box": {
                    "x1": round(x1, 2),
                    "y1": round(y1, 2),
                    "x2": round(x2, 2),
                    "y2": round(y2, 2),
                },
                "label": model.names[int(boxes.cls[i])],
                "class_id": int(boxes.cls[i]),
                "confidence": round(float(boxes.conf[i]), 4),
            })

    h, w = image.shape[:2]
    return {
        "detections": detections,
        "inference_ms": round(inference_ms, 2),
        "image_shape": {"width": w, "height": h},
    }
```

### 5.2 — FastAPI Endpoint Accepting Image Upload

```python
# app/routers/detect.py
import hashlib
import io
import json
import logging
from typing import Annotated

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from pydantic import BaseModel

from app.services.cache import get_cached_result, set_cached_result
from app.services.inference import run_inference
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/detect", tags=["Detection"])


# ── Response schema ──────────────────────────────────────────────────────────
class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class Detection(BaseModel):
    box: BoundingBox
    label: str
    class_id: int
    confidence: float

class DetectionResponse(BaseModel):
    detections: list[Detection]
    inference_ms: float
    image_shape: dict
    model_version: str
    cached: bool = False


# ── Helper: decode uploaded bytes to OpenCV array ────────────────────────────
def _bytes_to_bgr(data: bytes) -> np.ndarray:
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not decode image. Ensure it is a valid JPEG, PNG, or BMP.",
        )
    return img


# ── Main detect endpoint ─────────────────────────────────────────────────────
@router.post("/image", response_model=DetectionResponse, status_code=status.HTTP_200_OK)
async def detect_image(
    file: Annotated[UploadFile, File(description="Image file (JPEG/PNG/BMP, max 10 MB)")],
    conf: Annotated[float, Query(ge=0.01, le=1.0)] = 0.25,
    iou: Annotated[float, Query(ge=0.01, le=1.0)] = 0.45,
):
    """Detect objects in a single uploaded image.

    Returns bounding boxes, labels, and confidence scores.
    Results are cached in Redis for 60 seconds using an MD5 image hash as key.
    """
    # Enforce file size limit (10 MB)
    MAX_SIZE = 10 * 1024 * 1024
    raw = await file.read()
    if len(raw) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="Image exceeds 10 MB limit.")

    # Check Redis cache using MD5 hash of raw bytes + inference params
    cache_key = hashlib.md5(raw + f"{conf}{iou}".encode()).hexdigest()
    cached = await get_cached_result(cache_key)
    if cached:
        logger.debug("Cache HIT for key %s", cache_key)
        response = DetectionResponse(**json.loads(cached), cached=True)
        return response

    # Decode and run inference
    image = _bytes_to_bgr(raw)
    result = run_inference(image, conf_threshold=conf, iou_threshold=iou)

    response_data = {
        **result,
        "model_version": settings.ACTIVE_MODEL_VERSION,
        "cached": False,
    }
    # Cache for 60 seconds (adjust TTL based on use-case)
    await set_cached_result(cache_key, json.dumps(response_data), ttl=60)

    return DetectionResponse(**response_data)
```

### 5.3 — ONNX Export Script

```python
# training/export_onnx.py
"""
Export a trained YOLOv8 .pt model to ONNX format with dynamic batching.

Usage:
    python export_onnx.py \
        --weights runs/detect/train/weights/best.pt \
        --output artifacts/yolov8_custom.onnx \
        --imgsz 640 \
        --opset 17
"""
import argparse
from pathlib import Path

import onnx
import onnxsim
from ultralytics import YOLO


def export_to_onnx(
    weights: str,
    output: str,
    imgsz: int = 640,
    opset: int = 17,
    simplify: bool = True,
    dynamic: bool = True,
) -> Path:
    """Export YOLOv8 weights to ONNX.

    Parameters
    ----------
    weights  : Path to .pt file (e.g., best.pt from a training run)
    output   : Destination .onnx path
    imgsz    : Inference image size (must match training)
    opset    : ONNX opset version — 17 works with ORT 1.17+
    simplify : Run onnxsim to fold constants and simplify graph
    dynamic  : Enable dynamic batch size (recommended for servers)
    """
    model = YOLO(weights)

    # Ultralytics export wraps the full postprocessing inside the graph
    # Set `simplify=False` if you need raw output tensors for custom NMS
    exported = model.export(
        format="onnx",
        imgsz=imgsz,
        opset=opset,
        simplify=simplify,
        dynamic=dynamic,
        half=False,          # Export FP32 first; quantize separately
    )
    print(f"[export] ONNX model saved to: {exported}")

    # Verify the graph is well-formed
    onnx_model = onnx.load(exported)
    onnx.checker.check_model(onnx_model)
    print("[export] ONNX graph check passed.")

    # Optional: run onnx-simplifier for cleaner graph (better TRT compatibility)
    if simplify:
        simplified, ok = onnxsim.simplify(onnx_model)
        if ok:
            onnx.save(simplified, output)
            print(f"[export] Simplified ONNX saved to: {output}")
        else:
            print("[export] Simplification failed; saving original.")
            onnx.save(onnx_model, output)
    else:
        onnx.save(onnx_model, output)

    return Path(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--opset", type=int, default=17)
    args = parser.parse_args()
    export_to_onnx(args.weights, args.output, args.imgsz, args.opset)
```

### 5.4 — INT8 Quantization with ONNX Runtime

```python
# training/quantize.py
"""
Apply INT8 static quantization to a YOLOv8 ONNX model.

Static quantization requires a calibration dataset (~200 representative images).
Accuracy drop is typically < 1% mAP with a good calibration set.

Usage:
    python quantize.py \
        --model artifacts/yolov8_custom.onnx \
        --calib-dir data/calibration/ \
        --output artifacts/yolov8_custom_int8.onnx
"""
import argparse
from pathlib import Path

import cv2
import numpy as np
from onnxruntime.quantization import (
    CalibrationDataReader,
    QuantFormat,
    QuantType,
    quantize_static,
)


# ── Calibration data reader ──────────────────────────────────────────────────
class YOLOCalibrationReader(CalibrationDataReader):
    """Feeds calibration images to the ONNX Runtime quantizer."""

    def __init__(self, calib_dir: str, imgsz: int = 640, max_images: int = 200):
        self.image_paths = list(Path(calib_dir).glob("**/*.jpg"))[:max_images]
        self.image_paths += list(Path(calib_dir).glob("**/*.png"))[:max_images]
        self.image_paths = self.image_paths[:max_images]
        self.imgsz = imgsz
        self._iter = iter(self._generate())
        print(f"[calib] Using {len(self.image_paths)} calibration images.")

    def _preprocess(self, path: Path) -> np.ndarray:
        """Letterbox resize → normalise → CHW float32."""
        img = cv2.imread(str(path))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (self.imgsz, self.imgsz))
        img = img.astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))   # HWC → CHW
        return img[np.newaxis, ...]            # Add batch dim

    def _generate(self):
        for p in self.image_paths:
            yield {"images": self._preprocess(p)}

    def get_next(self):
        return next(self._iter, None)


def quantize_model(model_path: str, calib_dir: str, output_path: str):
    reader = YOLOCalibrationReader(calib_dir, imgsz=640, max_images=200)

    quantize_static(
        model_input=model_path,
        model_output=output_path,
        calibration_data_reader=reader,
        quant_format=QuantFormat.QDQ,       # QDQ format — best for TRT compatibility
        activation_type=QuantType.QInt8,
        weight_type=QuantType.QInt8,
        per_channel=True,                   # Per-channel weights = better accuracy
        reduce_range=True,                  # Recommended for AVX-512 systems
    )
    print(f"[quantize] INT8 model saved to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--calib-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    quantize_model(args.model, args.calib_dir, args.output)
```

### 5.5 — Batched Inference Implementation

```python
# app/services/batch_inference.py
"""
Batched ONNX Runtime inference for high-throughput scenarios.

Rather than running each image individually, we collect images into a batch
and execute a single forward pass — dramatically improving GPU utilisation.
"""
import asyncio
import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import onnxruntime as ort


@dataclass
class InferenceRequest:
    image: np.ndarray
    future: asyncio.Future = field(default_factory=asyncio.Future)


class BatchInferenceEngine:
    """Collects requests and processes them in batches using ONNX Runtime.

    Parameters
    ----------
    model_path   : Path to the ONNX model file
    max_batch    : Maximum batch size (limited by GPU VRAM)
    wait_ms      : Max milliseconds to wait before flushing an incomplete batch
    imgsz        : Expected square image size
    """

    def __init__(
        self,
        model_path: str,
        max_batch: int = 8,
        wait_ms: float = 20.0,
        imgsz: int = 640,
    ):
        self.max_batch = max_batch
        self.wait_ms = wait_ms / 1000.0
        self.imgsz = imgsz
        self._queue: asyncio.Queue[InferenceRequest] = asyncio.Queue()

        # Prefer CUDA EP; fall back to CPU
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
        sess_opts = ort.SessionOptions()
        sess_opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        sess_opts.intra_op_num_threads = 4
        self._session = ort.InferenceSession(model_path, sess_opts, providers=providers)
        self._input_name = self._session.get_inputs()[0].name

    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        """Resize, normalise, and convert to float32 CHW."""
        import cv2
        img = cv2.resize(image, (self.imgsz, self.imgsz))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        return np.transpose(img, (2, 0, 1))  # CHW

    async def infer(self, image: np.ndarray) -> Any:
        """Submit a single image for batched inference (async)."""
        req = InferenceRequest(image=image)
        await self._queue.put(req)
        return await req.future

    async def run_loop(self):
        """Background coroutine — collects requests and fires batched inference."""
        loop = asyncio.get_event_loop()
        while True:
            # Wait for first item
            batch: list[InferenceRequest] = [await self._queue.get()]
            deadline = loop.time() + self.wait_ms

            # Drain the queue up to max_batch or until deadline
            while len(batch) < self.max_batch:
                remaining = deadline - loop.time()
                if remaining <= 0:
                    break
                try:
                    req = await asyncio.wait_for(self._queue.get(), timeout=remaining)
                    batch.append(req)
                except asyncio.TimeoutError:
                    break

            # Build batch tensor  [B, C, H, W]
            tensors = np.stack([self._preprocess(r.image) for r in batch])

            t0 = time.perf_counter()
            outputs = await loop.run_in_executor(
                None,
                lambda: self._session.run(None, {self._input_name: tensors}),
            )
            elapsed_ms = (time.perf_counter() - t0) * 1000

            # Distribute results back to waiting coroutines
            for i, req in enumerate(batch):
                # outputs[0] shape: [B, num_preds, 85]
                req.future.set_result({
                    "raw_output": outputs[0][i],
                    "inference_ms": round(elapsed_ms / len(batch), 2),
                })
```

### 5.6 — Fine-Tuning Script with Custom Dataset

```python
# training/train.py
"""
YOLOv8 fine-tuning script for custom datasets.

Assumes data.yaml has been generated and calibration images are ready.
This script is invoked by a Celery task after a customer uploads their dataset.

Usage:
    python train.py \
        --data data/customer_42/data.yaml \
        --base-model yolov8s.pt \
        --epochs 100 \
        --batch 16 \
        --imgsz 640 \
        --job-id customer_42_run_001
"""
import argparse
import json
import shutil
from pathlib import Path

import mlflow
from ultralytics import YOLO


def train(
    data_yaml: str,
    base_model: str = "yolov8s.pt",   # n < s < m < l < x (speed vs accuracy)
    epochs: int = 100,
    batch: int = 16,
    imgsz: int = 640,
    device: str = "0",               # GPU index or "cpu"
    job_id: str = "run",
    mlflow_tracking_uri: str = "http://mlflow:5000",
) -> dict:
    """Fine-tune YOLOv8 and log the run to MLflow."""

    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment("visionguard-custom-training")

    with mlflow.start_run(run_name=job_id):
        # Log hyperparameters
        mlflow.log_params({
            "base_model": base_model,
            "epochs": epochs,
            "batch": batch,
            "imgsz": imgsz,
            "data_yaml": data_yaml,
        })

        model = YOLO(base_model)

        results = model.train(
            data=data_yaml,
            epochs=epochs,
            batch=batch,
            imgsz=imgsz,
            device=device,
            patience=20,              # Early stopping if no improvement for 20 epochs
            save=True,
            save_period=10,           # Checkpoint every 10 epochs
            val=True,
            augment=True,
            hsv_h=0.015,             # Colour augmentation
            hsv_s=0.7,
            hsv_v=0.4,
            fliplr=0.5,
            mosaic=1.0,              # Mosaic augmentation (very helpful with small datasets)
            mixup=0.1,
            degrees=10.0,            # Rotation
            translate=0.1,
            scale=0.5,
            project="runs/detect",
            name=job_id,
        )

        # Parse evaluation metrics from results
        metrics = {
            "mAP50": round(results.results_dict.get("metrics/mAP50(B)", 0), 4),
            "mAP50_95": round(results.results_dict.get("metrics/mAP50-95(B)", 0), 4),
            "precision": round(results.results_dict.get("metrics/precision(B)", 0), 4),
            "recall": round(results.results_dict.get("metrics/recall(B)", 0), 4),
        }
        mlflow.log_metrics(metrics)

        best_weights = Path(f"runs/detect/{job_id}/weights/best.pt")

        # Quality gate: reject if mAP@50 is below threshold
        MAP50_THRESHOLD = 0.65
        if metrics["mAP50"] < MAP50_THRESHOLD:
            raise ValueError(
                f"Training failed quality gate: mAP@50={metrics['mAP50']:.3f} "
                f"< threshold {MAP50_THRESHOLD}"
            )

        # Log the best weights as an MLflow artifact
        mlflow.log_artifact(str(best_weights), artifact_path="weights")
        print(f"[train] Job {job_id} completed. Metrics: {json.dumps(metrics, indent=2)}")
        return {"metrics": metrics, "weights": str(best_weights)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--base-model", default="yolov8s.pt")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--job-id", default="run")
    args = parser.parse_args()

    train(
        data_yaml=args.data,
        base_model=args.base_model,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        job_id=args.job_id,
    )
```

### 5.7 — Redis Caching for Repeated Detections

```python
# app/services/cache.py
"""
Redis-backed result cache.

Images from surveillance cameras often repeat near-identical frames.
Caching on MD5 of raw bytes gives a 30-40% cache hit rate in typical
CCTV workloads — dramatically reducing GPU load.
"""
import json
import logging
from typing import Any

import redis.asyncio as aioredis

from app.config import settings

logger = logging.getLogger(__name__)

# Module-level pool — shared across all FastAPI workers in the same process
_redis_pool: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.REDIS_URL,           # e.g. redis://redis:6379/0
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
        )
    return _redis_pool


async def get_cached_result(key: str) -> str | None:
    """Return cached JSON string or None on miss / error."""
    try:
        redis = await get_redis()
        value = await redis.get(f"vg:detect:{key}")
        if value:
            logger.debug("Cache HIT: %s", key)
        return value
    except Exception as exc:
        # Never let cache errors break the inference path
        logger.warning("Redis GET failed (key=%s): %s", key, exc)
        return None


async def set_cached_result(key: str, value: str, ttl: int = 60) -> None:
    """Store result JSON with a TTL. Errors are swallowed — cache is best-effort."""
    try:
        redis = await get_redis()
        await redis.setex(f"vg:detect:{key}", ttl, value)
        logger.debug("Cache SET: %s (TTL=%ds)", key, ttl)
    except Exception as exc:
        logger.warning("Redis SET failed (key=%s): %s", key, exc)


async def invalidate_model_cache() -> int:
    """Flush all cached detections when a new model is activated.

    Returns the number of keys deleted.
    """
    try:
        redis = await get_redis()
        keys = await redis.keys("vg:detect:*")
        if keys:
            deleted = await redis.delete(*keys)
            logger.info("Invalidated %d cached results after model swap.", deleted)
            return deleted
        return 0
    except Exception as exc:
        logger.error("Cache invalidation failed: %s", exc)
        return 0
```

---

## 6. Custom Training Guide

### 6.1 Labeling with Roboflow / CVAT

#### Roboflow (Recommended for Teams)

1. Create a free workspace at [roboflow.com](https://roboflow.com).
2. Upload raw images (drag-and-drop, or via `roboflow` Python SDK).
3. Annotate using the web editor: draw bounding boxes, assign class labels.
4. Apply a **preprocessing pipeline**: auto-orient, resize to 640×640.
5. Apply an **augmentation pipeline** (optional at labeling stage — YOLOv8 handles this during training):
   - Flip horizontal, ±15° rotation, ±25% brightness, blur.
6. Export in **YOLOv8** format → downloads a ZIP containing:
   ```
   dataset/
   ├── data.yaml
   ├── train/
   │   ├── images/  (*.jpg)
   │   └── labels/  (*.txt)
   ├── valid/
   │   ├── images/
   │   └── labels/
   └── test/
       ├── images/
       └── labels/
   ```

#### CVAT (Self-Hosted, More Control)

```bash
# Start CVAT locally with Docker Compose
git clone https://github.com/opencv/cvat.git
cd cvat
docker compose up -d

# Access the annotation UI at http://localhost:8080
# Export: Tasks → Export → YOLO 1.1 format
```

Convert CVAT XML to YOLO format if needed:

```bash
pip install datumaro
datum convert -i cvat_export/ -f cvat -o yolo_export/ -f yolo
```

### 6.2 `data.yaml` Configuration

```yaml
# data/customer_42/data.yaml
# Paths are relative to this file OR absolute paths

path: /workspace/data/customer_42   # Root dataset directory

train: train/images
val:   valid/images
test:  test/images                  # Optional

# Number of classes
nc: 4

# Class names — order must match the integer IDs in label files
names:
  0: dented_can
  1: missing_label
  2: crushed_box
  3: foreign_object

# Optional: class weights for imbalanced datasets
# class_weights: [1.0, 2.5, 1.0, 3.0]
```

### 6.3 YOLOv8 Training Command and Configuration

```bash
# Quick start — single GPU
yolo detect train \
  model=yolov8s.pt \
  data=data/customer_42/data.yaml \
  epochs=100 \
  imgsz=640 \
  batch=16 \
  device=0 \
  patience=20 \
  optimizer=AdamW \
  lr0=0.001 \
  lrf=0.01 \
  weight_decay=0.0005 \
  warmup_epochs=3.0 \
  cos_lr=True \
  mosaic=1.0 \
  mixup=0.1 \
  project=runs/detect \
  name=customer_42_v1 \
  exist_ok=False \
  verbose=True

# Multi-GPU training (DDP)
yolo detect train \
  model=yolov8m.pt \
  data=data/customer_42/data.yaml \
  device=0,1 \
  batch=32 \
  epochs=150
```

**Tips for small datasets (< 500 images):**
- Start from `yolov8n.pt` or `yolov8s.pt` (smaller models overfit less).
- Increase `mosaic=1.0` and `copy_paste=0.3` augmentation.
- Lower `lr0` to `0.0005` — large datasets need larger initial LR.
- Set `freeze=10` to freeze the first 10 backbone layers and only train the head.

### 6.4 Evaluation Metrics

| Metric | Formula | What It Means | Target |
|---|---|---|---|
| **mAP@50** | Mean AP at IoU ≥ 0.50 | Standard detection metric | > 0.75 (custom domain) |
| **mAP@50-95** | Mean AP averaged over IoU 0.50–0.95 | Stricter, COCO-style | > 0.55 |
| **Precision** | TP / (TP + FP) | False alarm rate | > 0.80 |
| **Recall** | TP / (TP + FN) | Miss rate | > 0.80 |
| **F1 Score** | 2·P·R / (P+R) | Harmonic mean | > 0.80 |
| **IoU** | Area(A∩B) / Area(A∪B) | Box quality | ≥ 0.50 |

Evaluate your trained model:

```bash
yolo detect val \
  model=runs/detect/customer_42_v1/weights/best.pt \
  data=data/customer_42/data.yaml \
  split=test \
  conf=0.001 \
  iou=0.6 \
  plots=True

# Results saved to runs/detect/val/
# ─ confusion_matrix.png
# ─ PR_curve.png
# ─ results.csv
```

---

## 7. Optimization & Benchmarks

### 7.1 GPU vs CPU Latency Comparison

Tested on: YOLOv8s model, 640×640 input, single image inference  
Hardware: NVIDIA A100 40 GB (cloud), AMD EPYC 7763 64-core (cloud CPU), Jetson Orin NX

| Backend | Hardware | Precision | Latency (ms) | Throughput (FPS) | Memory |
|---|---|---|---|---|---|
| PyTorch | A100 GPU | FP32 | 8.2 | 122 | 4.1 GB |
| ONNX Runtime | A100 (CUDA EP) | FP32 | 6.1 | 164 | 1.8 GB |
| ONNX Runtime | A100 (CUDA EP) | FP16 | 3.8 | 263 | 0.9 GB |
| ONNX Runtime | A100 (CUDA EP) | INT8 | 2.9 | 345 | 0.6 GB |
| Triton (TensorRT) | A100 | FP16 | 2.1 | 476 | 0.7 GB |
| ONNX Runtime | CPU (64-core) | FP32 | 42.0 | 24 | 0.5 GB |
| ONNX Runtime | CPU (64-core) | INT8 | 18.5 | 54 | 0.3 GB |
| ONNX Runtime | Jetson Orin NX | FP16 | 21.0 | 48 | 0.4 GB |
| ONNX Runtime (TRT EP) | Jetson Orin NX | INT8 | 9.5 | 105 | 0.2 GB |
| ONNX Runtime | Raspberry Pi 4 | INT8 | 890 | 1.1 | 0.3 GB |

> **Key takeaway:** TRT EP on Jetson Orin achieves 105 FPS at INT8 — enough for real-time multi-camera edge deployment without cloud round-trips.

### 7.2 INT8 Quantization Accuracy vs Speed Tradeoff

Evaluated on internal 4-class defect detection dataset (2,400 test images):

| Precision | mAP@50 | mAP@50-95 | Latency (ms, CPU) | Size (MB) |
|---|---|---|---|---|
| FP32 (baseline) | 0.874 | 0.621 | 42.0 | 22.4 |
| FP16 | 0.872 | 0.619 | 27.3 | 11.2 |
| INT8 (dynamic) | 0.861 | 0.608 | 18.5 | 5.8 |
| INT8 (static, 200 cal) | 0.869 | 0.618 | 18.5 | 5.8 |
| INT8 (static, 50 cal) | 0.841 | 0.592 | 18.5 | 5.8 |

> **Key takeaway:** Static INT8 with ≥200 calibration images loses < 1% mAP while delivering 2.3× CPU speedup. Dynamic INT8 (no calibration data needed) is fast to apply but can lose 1–3% mAP.

### 7.3 Batched Inference Throughput

Tested with ONNX Runtime CUDA EP, YOLOv8s, A100:

| Batch Size | Total Images | Wall Time (ms) | FPS | GPU Util |
|---|---|---|---|---|
| 1 | 1,000 | 6,100 | 164 | 31% |
| 4 | 1,000 | 2,200 | 455 | 72% |
| 8 | 1,000 | 1,450 | 690 | 91% |
| 16 | 1,000 | 1,280 | 781 | 98% |
| 32 | 1,000 | 1,310 | 763 | 98% |

> **Key takeaway:** Batch size 8–16 is the sweet spot. Beyond 16, GPU is saturated and latency per image plateaus. First-response latency (time to first result) increases linearly with batch size — trade off with your SLA.

---

## 8. Deployment

### 8.1 Dockerfile (FastAPI + YOLO)

```dockerfile
# Dockerfile
# Multi-stage build: keeps final image lean by separating build deps

# ── Stage 1: Builder ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libglib2.0-0 libgl1-mesa-glx libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ── Stage 2: Runtime ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Non-root user for security
RUN groupadd -r visionguard && useradd -r -g visionguard visionguard

# Runtime system libs (OpenCV needs libGL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libgl1-mesa-glx libsm6 libxext6 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /home/visionguard/.local

WORKDIR /app
COPY --chown=visionguard:visionguard app/ ./app/
COPY --chown=visionguard:visionguard artifacts/ ./artifacts/

# Pre-download YOLOv8 weights (baked into image; avoids cold-start download)
RUN python -c "from ultralytics import YOLO; YOLO('yolov8s.pt')"

ENV PATH=/home/visionguard/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER visionguard
EXPOSE 8000

# Gunicorn with Uvicorn workers: 1 worker per vCPU
CMD ["gunicorn", "app.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--access-logfile", "-"]
```

Build and run locally:

```bash
docker build -t visionguard:latest .
docker run --gpus all -p 8000:8000 \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host.docker.internal/visionguard \
  -e ACTIVE_MODEL_VERSION=v2.1 \
  visionguard:latest
```

### 8.2 Triton Inference Server Configuration

```
triton_models/
├── yolov8s_fp16/
│   ├── config.pbtxt
│   └── 1/
│       └── model.onnx           ← Symlink or copy your .onnx here
└── yolov8s_int8/
    ├── config.pbtxt
    └── 1/
        └── model.onnx
```

```protobuf
# triton_models/yolov8s_fp16/config.pbtxt
name: "yolov8s_fp16"
backend: "onnxruntime"
max_batch_size: 16

# Input tensor spec (matches YOLOv8 ONNX export with dynamic batch)
input [
  {
    name: "images"
    data_type: TYPE_FP32
    dims: [ 3, 640, 640 ]   # C, H, W — batch dim is implicit
  }
]

# Output tensor spec
output [
  {
    name: "output0"
    data_type: TYPE_FP32
    dims: [ -1, 84 ]         # [num_predictions, 4_box + 80_classes]
  }
]

# Dynamic batching — Triton will auto-batch requests within 10 ms
dynamic_batching {
  preferred_batch_size: [ 4, 8, 16 ]
  max_queue_delay_microseconds: 10000
}

# Use 2 model instances on the same GPU for pipelining
instance_group [
  {
    count: 2
    kind: KIND_GPU
    gpus: [ 0 ]
  }
]
```

Launch Triton:

```bash
docker run --gpus all --rm \
  -p 8500:8000 -p 8501:8001 -p 8502:8002 \
  -v $(pwd)/triton_models:/models \
  nvcr.io/nvidia/tritonserver:24.04-py3 \
  tritonserver \
    --model-repository=/models \
    --log-verbose=0 \
    --strict-model-config=false
```

### 8.3 Kubernetes Deployment YAML

```yaml
# k8s/visionguard-deployment.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: visionguard-api
  namespace: visionguard
  labels:
    app: visionguard-api
    version: "2.1"
spec:
  replicas: 3
  selector:
    matchLabels:
      app: visionguard-api
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0        # Zero-downtime rolling update
  template:
    metadata:
      labels:
        app: visionguard-api
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      containers:
        - name: api
          image: ghcr.io/your-org/visionguard:2.1.0
          imagePullPolicy: Always
          ports:
            - containerPort: 8000
          env:
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: visionguard-secrets
                  key: redis_url
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: visionguard-secrets
                  key: database_url
            - name: TRITON_HOST
              value: "triton-service:8001"  # gRPC
            - name: INFERENCE_BACKEND
              value: "triton"              # or "onnxruntime"
          resources:
            requests:
              cpu: "500m"
              memory: "1Gi"
            limits:
              cpu: "2000m"
              memory: "4Gi"
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 30
            failureThreshold: 3
---
apiVersion: v1
kind: Service
metadata:
  name: visionguard-api-service
  namespace: visionguard
spec:
  selector:
    app: visionguard-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: visionguard-api-hpa
  namespace: visionguard
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: visionguard-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Pods
      pods:
        metric:
          name: inference_queue_depth   # Custom Prometheus metric
        target:
          type: AverageValue
          averageValue: "5"
```

Apply:

```bash
kubectl create namespace visionguard
kubectl apply -f k8s/
kubectl rollout status deployment/visionguard-api -n visionguard
```

### 8.4 Edge Deployment: ONNX Runtime on Jetson Nano / Raspberry Pi

#### Jetson Orin NX (Recommended Edge GPU)

```bash
# Jetson runs JetPack 6.x (Ubuntu 22.04 base)
# Install ONNX Runtime with TensorRT EP from NVIDIA's wheel index

pip install \
  onnxruntime-gpu==1.18.0 \
  --extra-index-url https://pypi.ngc.nvidia.com

# Verify TRT EP is available
python -c "
import onnxruntime as ort
print(ort.get_available_providers())
# Should include 'TensorrtExecutionProvider', 'CUDAExecutionProvider'
"

# Build TensorRT engine from ONNX model (first run caches the plan)
python - <<'EOF'
import onnxruntime as ort
providers = [
    ('TensorrtExecutionProvider', {
        'trt_max_workspace_size': 1 << 30,     # 1 GB
        'trt_fp16_enable': True,
        'trt_engine_cache_enable': True,        # Cache compiled engine to disk
        'trt_engine_cache_path': '/opt/trt_cache',
    }),
    'CUDAExecutionProvider',
]
sess = ort.InferenceSession("yolov8s_int8.onnx", providers=providers)
print("Session ready:", sess.get_inputs()[0].shape)
EOF
```

#### Raspberry Pi 4 (CPU-only, INT8)

```bash
# RPi 4 does NOT have a GPU — use the CPU EP only
pip install onnxruntime==1.18.0   # CPU-only build

# Optimise thread counts for 4-core ARM Cortex-A72
python - <<'EOF'
import onnxruntime as ort

opts = ort.SessionOptions()
opts.intra_op_num_threads = 4      # Use all 4 cores
opts.inter_op_num_threads = 1
opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
opts.optimized_model_filepath = "yolov8s_int8_rpi_optimized.onnx"  # Cache opt model

sess = ort.InferenceSession(
    "yolov8s_int8.onnx",
    sess_options=opts,
    providers=["CPUExecutionProvider"],
)
print("RPi session ready. Expected ~890ms/frame at 640x640.")
EOF

# Reduce input size to 320x320 for ~220ms/frame with mild accuracy loss
# Retrain/export with imgsz=320 for best results
```

---

## 9. Monitoring

### 9.1 Inference Latency Tracking (Prometheus + Grafana)

```python
# app/middleware/metrics.py
"""
Expose Prometheus metrics at GET /metrics.

Tracked:
  - inference_duration_seconds   : Histogram of per-request inference time
  - inference_requests_total     : Counter by status (success/error)
  - cache_hits_total             : Counter for Redis cache hits
  - active_model_info            : Gauge with model version label
  - detection_count              : Histogram of detections per image
"""
from prometheus_client import Counter, Gauge, Histogram, make_asgi_app

# ── Define metrics ────────────────────────────────────────────────────────────
INFERENCE_LATENCY = Histogram(
    "inference_duration_seconds",
    "End-to-end inference latency in seconds",
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
)
REQUEST_COUNTER = Counter(
    "inference_requests_total",
    "Total inference requests",
    ["status", "model_version"],
)
CACHE_HIT_COUNTER = Counter(
    "cache_hits_total",
    "Total Redis cache hits",
)
MODEL_INFO = Gauge(
    "active_model_info",
    "Currently active model",
    ["version", "backend"],
)
DETECTION_COUNT = Histogram(
    "detection_count_per_image",
    "Number of objects detected per image",
    buckets=[0, 1, 2, 5, 10, 20, 50],
)


def track_inference(latency_s: float, model_version: str, n_detections: int, ok: bool):
    """Call this after every inference request."""
    status = "success" if ok else "error"
    INFERENCE_LATENCY.observe(latency_s)
    REQUEST_COUNTER.labels(status=status, model_version=model_version).inc()
    if ok:
        DETECTION_COUNT.observe(n_detections)


# Mount Prometheus ASGI app at /metrics
metrics_app = make_asgi_app()
```

```python
# app/main.py (excerpt)
from fastapi import FastAPI
from app.middleware.metrics import metrics_app, MODEL_INFO
from app.config import settings

app = FastAPI(title="VisionGuard API", version="2.1.0")

# Mount Prometheus scrape endpoint
app.mount("/metrics", metrics_app)

@app.on_event("startup")
async def startup():
    # Pre-load model
    from app.services.inference import load_model
    load_model(settings.MODEL_WEIGHTS_PATH)
    # Update gauge with active model info
    MODEL_INFO.labels(
        version=settings.ACTIVE_MODEL_VERSION,
        backend=settings.INFERENCE_BACKEND,
    ).set(1)
```

Grafana dashboard panels to create:
- **p50 / p95 / p99 inference latency** — `histogram_quantile(0.95, inference_duration_seconds_bucket)`
- **Request rate** — `rate(inference_requests_total[5m])`
- **Error rate** — `rate(inference_requests_total{status="error"}[5m]) / rate(inference_requests_total[5m])`
- **Cache hit ratio** — `rate(cache_hits_total[5m]) / rate(inference_requests_total[5m])`
- **Detection volume heatmap** — `detection_count_per_image_bucket`

### 9.2 Accuracy Drift Detection

Model accuracy degrades silently as real-world data distribution shifts (new product packaging, seasonal lighting changes, camera repositioning). Detect this before customers notice:

```python
# monitoring/accuracy_monitor.py
"""
Periodically evaluate the active model on a held-out golden test set.
If mAP@50 drops below the alert threshold, send a Slack/PagerDuty alert.

Run as a Kubernetes CronJob every 6 hours.
"""
import json
import smtplib
from pathlib import Path

import mlflow
import requests
from ultralytics import YOLO


GOLDEN_TEST_YAML = "data/golden_test/data.yaml"
MAP50_ALERT_THRESHOLD = 0.72    # Alert if mAP@50 drops below this
MAP50_CRITICAL_THRESHOLD = 0.60 # Page on-call if it drops this low


def evaluate_current_model(weights_path: str) -> dict:
    model = YOLO(weights_path)
    results = model.val(
        data=GOLDEN_TEST_YAML,
        split="test",
        conf=0.001,
        iou=0.6,
        verbose=False,
    )
    return {
        "mAP50": results.results_dict["metrics/mAP50(B)"],
        "mAP50_95": results.results_dict["metrics/mAP50-95(B)"],
    }


def send_alert(message: str, level: str = "warning"):
    """Send alert to Slack webhook."""
    slack_url = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    icon = ":warning:" if level == "warning" else ":rotating_light:"
    requests.post(slack_url, json={"text": f"{icon} *VisionGuard Accuracy Alert*\n{message}"})


def run_drift_check(weights_path: str):
    print("[monitor] Evaluating current model on golden test set...")
    metrics = evaluate_current_model(weights_path)
    map50 = metrics["mAP50"]

    # Log to MLflow for trend tracking
    with mlflow.start_run(run_name="drift_check"):
        mlflow.log_metrics(metrics)

    print(f"[monitor] mAP@50 = {map50:.4f}")

    if map50 < MAP50_CRITICAL_THRESHOLD:
        send_alert(
            f"CRITICAL: mAP@50 = {map50:.3f} (threshold: {MAP50_CRITICAL_THRESHOLD}). "
            f"Model may be severely degraded. Immediate retraining required.",
            level="critical",
        )
    elif map50 < MAP50_ALERT_THRESHOLD:
        send_alert(
            f"WARNING: mAP@50 = {map50:.3f} (threshold: {MAP50_ALERT_THRESHOLD}). "
            f"Consider scheduling a retraining run.",
        )
    else:
        print(f"[monitor] Accuracy OK: mAP@50 = {map50:.3f}")


if __name__ == "__main__":
    run_drift_check("artifacts/best.pt")
```

### 9.3 Model Versioning with MLflow

```python
# app/services/model_registry.py
"""
Helper to fetch the Production-stage model URI from MLflow Model Registry
and load it at startup.
"""
import mlflow
from mlflow.tracking import MlflowClient

MLFLOW_TRACKING_URI = "http://mlflow:5000"
MODEL_NAME = "visionguard-detector"


def get_production_model_path() -> str:
    """Return the local path to the current Production model weights."""
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    client = MlflowClient()

    # Fetch the model version tagged as 'Production'
    versions = client.get_latest_versions(MODEL_NAME, stages=["Production"])
    if not versions:
        raise RuntimeError(f"No Production model found in registry: {MODEL_NAME}")

    latest = versions[0]
    print(f"[registry] Loading model: {MODEL_NAME} v{latest.version} "
          f"(run_id={latest.run_id})")

    # Download artifact to local cache
    artifact_path = client.download_artifacts(
        run_id=latest.run_id,
        path="weights/best.pt",
        dst_path="/tmp/model_cache",
    )
    return artifact_path


def promote_to_production(run_id: str, version: str):
    """Transition a model version to Production stage (and archive old one)."""
    client = MlflowClient()
    client.transition_model_version_stage(
        name=MODEL_NAME,
        version=version,
        stage="Production",
        archive_existing_versions=True,   # Automatically archive previous Production
    )
    print(f"[registry] Model v{version} promoted to Production.")
```

---

## 10. Production Gotchas

These are real issues encountered after deploying VisionGuard in live retail and manufacturing environments. Learn from them.

- **ONNX model input shape mismatch after export:** YOLOv8's ONNX export uses dynamic batch by default, but some early versions hardcoded batch=1. Always check `model.get_inputs()[0].shape` immediately after export. If batch is fixed, re-export with `dynamic=True`.

- **Letterboxing affects bounding box coordinates:** YOLOv8 letterboxes input images to preserve aspect ratio (adds grey padding bars). If you resize to 640×640 naively with `cv2.resize`, your bounding box coordinates will be wrong relative to the original image. Always use letterbox-aware coordinate scaling — Ultralytics provides `Results.orig_img` and handles this internally, but raw ONNX inference requires manual coordinate de-letterboxing.

- **Redis cache poisoning by resized images:** Two different clients sending "the same" image but at different resolutions (one 1920×1080, one 640×480) produce different MD5 hashes. Good — they should be separate cache entries. But if you resize images *before* hashing, you'll get false cache hits for images that look similar but were originally different. Hash the raw uploaded bytes before any preprocessing.

- **Celery training jobs time out on large datasets:** Default Celery task timeout is 300 seconds. YOLOv8 training on 10,000 images for 100 epochs can take 4–8 hours on a single GPU. Set `task_time_limit = 43200` (12 hours) and implement heartbeat pings so the broker doesn't mark the task as lost. Use `celery inspect active` to confirm the task is still alive.

- **GPU memory accumulation across requests:** If you retain PyTorch `Results` objects across multiple requests without calling `del results` and `torch.cuda.empty_cache()`, GPU memory will slowly grow. This is subtle — the service may run fine for hours then OOM. Keep your inference function self-contained and explicitly delete tensors after extracting values.

- **YOLO model "warm-up" latency:** The first inference call after loading is ~3–5× slower than subsequent calls due to CUDA kernel compilation and memory page faults. Always run 3–5 dummy forward passes during startup (in the `lifespan` context). Otherwise your first real user request gets a terrible latency spike that may trigger your health check to fail.

- **NMS threshold choice affects perceived accuracy:** A customer complained about "missing" detections. Root cause: `iou=0.45` was merging two overlapping boxes (e.g., two adjacent bottles on a shelf) into one. Adjusting to `iou=0.6` resolved it but introduced duplicate detections for large objects. NMS thresholds are use-case-specific — expose them as API parameters rather than hardcoding.

- **Triton model hot-swap causes brief inconsistency:** Updating the ONNX model file in Triton's repository while the server is running causes a brief window where some requests hit the old model and some hit the new one. Use Triton's model control API (`POST /v2/repository/models/{model}/load`) which does an atomic swap. Keep the old version directory available for instant rollback.

- **RTSP stream reconnection loops:** When ingesting RTSP camera streams, the stream will drop periodically (network glitch, camera reboot). A naive `while True: cap.read()` loop will spin at 100% CPU reading failed frames silently. Implement exponential backoff reconnection with a frame-validity check (`if not ret: reconnect_with_backoff()`).

- **INT8 quantization with per-channel enabled on old hardware:** `per_channel=True` in ONNX Runtime quantization uses AVX-512 instructions. Some older Intel Xeon servers (pre-Skylake) don't have AVX-512 — the inference worker will crash with an illegal instruction. Test on the exact target CPU and fall back to `per_channel=False` for old hardware.

---

## 11. Lessons Learned

### Start with the smallest YOLO variant that meets your accuracy target

We initially assumed bigger = better and deployed YOLOv8m everywhere. On profiling, 80% of our endpoints were camera feeds where YOLOv8s achieved identical business-level accuracy (because the detection targets were large, well-lit objects). Switching to `yolov8s` cut inference cost by 40% and freed GPU headroom for batching. Profile with your *actual* data before choosing model size.

### The labeling pipeline is your biggest bottleneck

We spent more engineering time on data labeling workflows, format conversions, and quality control than on any inference or API code. Roboflow was worth every dollar for its annotation consistency checks and auto-export in multiple formats. For future projects: budget 60% of the ML timeline for data, 20% for training, 20% for deployment.

### Redis cache hit rates were higher than expected

In retail CCTV workloads, consecutive video frames are near-identical (no motion, static shelf). Our 60-second MD5 cache achieved 35–45% hit rates during business hours, effectively cutting GPU usage by a third with zero accuracy tradeoff. Cache at the raw-bytes level — it's cheap and the wins are real.

### Custom fine-tuning UX is harder than fine-tuning itself

The technical pipeline was straightforward. The hard part was: What error message do you show when a customer's label file is malformed? What happens when training crashes mid-epoch? How do you present mAP@50 to a non-ML retail manager? We underestimated the UX and error-handling work by 3×. Treat the fine-tuning feature as a product, not just a script.

### MLflow model registry saved us from a regression disaster

After a seemingly routine retraining run, a model with a subtle data bug was promoted to production — it detected "missing label" class at 90% recall but 30% precision (enormous false-alarm rate). Because every model version was registered in MLflow with evaluation metrics, we caught the regression within minutes via our Grafana alert on false-positive rate. We rolled back to the previous registered version in under 2 minutes. Without the registry, this would have been a fire-fighting nightmare.

### Edge deployment is not just "export ONNX and copy the file"

Jetson devices have CUDA/TensorRT versions tightly coupled to JetPack versions. An ONNX exported on a workstation running CUDA 12.3 will not always produce a valid TensorRT engine on JetPack 5.x (CUDA 11.4). Build and validate your ONNX models on hardware that matches the target device, or use Triton's model conversion service. Also: TensorRT engine compilation (the first inference run) can take 10–15 minutes on Jetson. Account for this in your edge provisioning script.

### Monitoring inference latency p99, not just average

Average latency looked healthy (18ms). p99 latency was 1.2 seconds — occasional GC pauses and Redis connection pool saturation caused tail latency spikes. These p99 spikes triggered alert rules that caused downstream applications to time out. Always monitor and alert on p99 (and p99.9 for SLA-sensitive clients).

### The quality gate in the training pipeline is non-negotiable

Early on, we skipped the mAP quality gate to "iterate faster." A customer received a model update that had been trained on their uploaded data, but the data had accidentally contained mislabeled images. The model performed worse than the generic COCO model and the customer blamed us. After reinstating the gate (`mAP50 >= 0.65` to pass), auto-reject happened 3 times in the following month — catching bad data before it could reach production.

---

*Last updated: May 2026 | Stack versions as of YOLOv8 8.2.x, ONNX Runtime 1.18.x, FastAPI 0.111.x*
