# Batch 8 — Computer Vision
> Teaching machines to see, understand, and generate images.

---

## 1. Image Classification

**Definition**  
Given an image, the model outputs a single label (or ranked list of labels) describing what's in it. It answers "what is this?" — not where or how many.

**Real-World Dev Example**  
A plant disease app sends a leaf photo to a ResNet-50 model; it returns `"Powdery Mildew (92% confidence)"`.

**ASCII Diagram**
```
[Image: 224x224] --> [CNN Backbone] --> [Flatten] --> [Dense] --> "Cat"
```

### Gotchas & Dev Context
- Classifies the **whole image** — fails if multiple subjects compete for the label.
- Input images must be resized to model's expected dimensions (e.g., 224×224 for ResNet).
- Softmax output sums to 1.0; always check top-5, not just top-1 accuracy.
- Class imbalance (1000 cats, 50 dogs) will bias the model — use weighted loss or oversample.

### Production FAQ
**Q: My model is 98% accurate on test data but poor in prod — why?**  
A: Training and prod images differ (different camera, lighting, resolution). This is **distribution shift** — add real-world images to training data.

**Q: Should I use accuracy or F1 for a medical classifier?**  
A: Use F1 or AUC-ROC. Accuracy is misleading on imbalanced datasets (e.g., 99% "healthy" trivially gets 99% accuracy).

---

## 2. Object Detection (YOLO, SSD, Faster R-CNN)

**Definition**  
Finds *where* objects are in an image by drawing bounding boxes and labelling each one. Answers both "what?" and "where?".

**Real-World Dev Example**  
A warehouse robot uses YOLOv8 to detect boxes, pallets, and forklifts in real-time camera frames at 60 FPS.

**ASCII Diagram**
```
Input Image
  └──> Backbone (feature extraction)
         └──> Detection Head
                ├── [Box: x,y,w,h]
                └── [Class: "Forklift" 87%]
```

### Gotchas & Dev Context
- **YOLO**: Fastest, single-pass, great for real-time. Struggles with tiny/dense objects.
- **SSD**: Multi-scale anchors, slightly slower than YOLO, better for varied object sizes.
- **Faster R-CNN**: Two-stage (propose regions → classify). Most accurate, but slowest.
- **IoU (Intersection over Union)** measures box quality — typical threshold is 0.5.
- NMS (Non-Max Suppression) removes duplicate boxes; tune its threshold carefully.
- mAP (mean Average Precision) is the standard eval metric.

### Production FAQ
**Q: YOLO misses small objects in drone footage — fix?**  
A: Use a higher-resolution input, tile large images into patches before inference, or switch to YOLOv8-nano with a P2 detection head.

**Q: When should I pick Faster R-CNN over YOLO?**  
A: When accuracy matters more than speed — e.g., medical imaging or forensics, not live video.

---

## 3. Semantic Segmentation

**Definition**  
Labels every pixel in an image with a class (sky, road, car, person) but doesn't distinguish between individual instances — all cars are the same colour.

**Real-World Dev Example**  
An autonomous driving system uses DeepLab to colour every pixel: road = grey, pedestrian = red, sky = blue — used to plan safe paths.

**ASCII Diagram**
```
Input Image          Output Mask
┌─────────────┐      ┌─────────────┐
│  🚗  🌳  🏠 │ -->  │  🟥  🟩  🟦 │
│   road sky  │      │  per sky rd │
└─────────────┘      └─────────────┘
```

### Gotchas & Dev Context
- Output is a pixel-class map — same spatial size as input.
- Common models: **FCN**, **DeepLabV3+**, **SegFormer**.
- Metric: **mIoU** (mean Intersection over Union per class).
- Class imbalance is brutal — sky occupies 40% of pixels, small signs 0.01%.
- Use **dilated convolutions** to preserve spatial resolution without losing context.

### Production FAQ
**Q: mIoU looks good but road edges are jagged — how to sharpen?**  
A: Use a CRF (Conditional Random Field) post-processing step or switch to a decoder with skip connections (e.g., DeepLab ASPP).

**Q: Semantic vs instance segmentation — which for crowd counting?**  
A: Instance segmentation — semantic treats all "persons" as one blob, making counting impossible.

---

## 4. Instance Segmentation (Mask R-CNN)

**Definition**  
Like semantic segmentation but each object instance gets its own separate mask — two dogs are two distinct coloured regions, not one.

**Real-World Dev Example**  
A recycling sorting robot uses Mask R-CNN to find the pixel-precise boundary of each bottle on a conveyor belt to drive the robotic arm.

**ASCII Diagram**
```
Image --> Backbone --> RPN (Region Proposals)
                          └--> ROI Align
                                  ├── Class head  -> "Bottle"
                                  ├── Box head    -> [x,y,w,h]
                                  └── Mask head   -> 28×28 binary mask
```

### Gotchas & Dev Context
- Built on Faster R-CNN + an extra **mask branch**.
- Slower than YOLO-seg but masks are higher quality.
- `ROI Align` (vs ROI Pool) is critical — prevents misalignment artifacts.
- Mask quality depends on **mask head resolution**; default 28×28 is often too coarse for thin objects.
- Panoptic segmentation = semantic + instance in one pass.

### Production FAQ
**Q: Mask R-CNN is too slow for our edge device — alternatives?**  
A: Try **YOLOv8-seg** or **YOLO-NAS-seg** — they offer instance masks at near-YOLO speed.

**Q: How do I handle overlapping instances?**  
A: Masks are predicted independently per ROI; NMS filters duplicate boxes, and overlapping masks are rendered in Z-order by confidence score.

---

## 5. Image Generation (Stable Diffusion, DALL·E, Midjourney)

**Definition**  
AI models that create brand-new images from a text prompt or reference image. They learn patterns from millions of image-text pairs and synthesise new visuals.

**Real-World Dev Example**  
A game studio uses Stable Diffusion locally to generate 500 concept art variants from "dark fantasy castle at sunset" in minutes instead of commissioning artists for each.

### Gotchas & Dev Context
- **Stable Diffusion**: Open-source, runs locally (GPU ≥6 GB VRAM), highly customisable via LoRA/ControlNet.
- **DALL·E 3**: OpenAI API, excellent prompt adherence, closed weights.
- **Midjourney**: Best aesthetic quality out-of-the-box, Discord/API only, no local run.
- Prompt engineering matters enormously — add style tokens like `"photorealistic, 8K, cinematic lighting"`.
- Generated images may inherit training data biases (e.g., stereotyped representations).
- Copyright/ownership of AI-generated images is still legally grey in most jurisdictions.

### Production FAQ
**Q: Stable Diffusion generates blurry faces — how to fix?**  
A: Use a face-restoration post-processor like **GFPGAN** or **CodeFormer**, or load a fine-tuned face model (e.g., RealisticVision).

**Q: Can I fine-tune Stable Diffusion on my brand's style?**  
A: Yes — use **DreamBooth** (5–20 reference images) or **LoRA** (lightweight adapter, <200 MB) for style/character fine-tuning.

---

## 6. Diffusion Models

**Definition**  
A generative model that learns to reverse a gradual noising process — it's trained by adding Gaussian noise step-by-step to images, then learning to denoise them back.

**Real-World Dev Example**  
Stable Diffusion uses a diffusion model in latent space; during inference it starts with pure noise and runs ~20–50 denoising steps guided by your text prompt.

**ASCII Diagram**
```
Training:   Clean Image --> [+noise x T steps] --> Pure Noise
Inference:  Pure Noise  --> [denoise x T steps] --> Generated Image
                                   ↑
                            (guided by text)
```

### Gotchas & Dev Context
- Diffusion is slower than GANs (requires multiple denoising steps) but far more stable to train.
- **DDPM** (original), **DDIM** (faster, ~10 steps), **DPM-Solver** (even faster) are common schedulers.
- **Classifier-Free Guidance (CFG)**: CFG scale 7–12 balances creativity vs prompt adherence.
- Higher step count ≠ always better; 20 DDIM steps often matches 100 DDPM steps.

### Production FAQ
**Q: How do I speed up inference?**  
A: Use DDIM or DPM-Solver++ schedulers (10–25 steps vs 1000), enable half-precision (`fp16`), and use latent diffusion instead of pixel-space diffusion.

**Q: What's the difference between pixel-space and latent diffusion?**  
A: Pixel-space runs denoising directly on image pixels (slow, memory-hungry). Latent diffusion (Stable Diffusion) denoises in a compressed latent space then decodes — ~4–8× faster.

---

## 7. Latent Space

**Definition**  
A compressed, lower-dimensional numerical representation of data learned by a model — the "abstract coordinate system" where similar concepts cluster together.

**Real-World Dev Example**  
In Stable Diffusion, a 512×512 image is encoded into a 64×64×4 latent tensor. All denoising happens in this small space, then a VAE decoder expands it back to full resolution.

**ASCII Diagram**
```
Image (512×512×3)
      │ Encoder
      ▼
Latent (64×64×4)  <-- diffusion/editing happens here
      │ Decoder
      ▼
Image (512×512×3)
```

### Gotchas & Dev Context
- Arithmetic in latent space is meaningful: `latent("king") - latent("man") + latent("woman") ≈ latent("queen")`.
- Moving smoothly between two latents = **interpolation** (creates morphing effects).
- Out-of-distribution latents decode to garbled images — stay near the trained manifold.
- Used in VAEs, GANs, diffusion models, and representation learning.

### Production FAQ
**Q: Why does image editing in latent space sometimes cause artifacts?**  
A: The VAE decoder isn't perfect — it can hallucinate textures. Use higher-quality VAEs (e.g., SDXL's improved VAE) or fp32 decoding.

**Q: Can I search/retrieve images using latent vectors?**  
A: Yes — encode all images to latents (or CLIP embeddings), store in a vector DB, and do nearest-neighbour search. This is how reverse image search works.

---

## 8. U-Net

**Definition**  
A CNN architecture shaped like a "U" with a contracting encoder path and an expanding decoder path connected by skip connections — originally designed for biomedical image segmentation.

**Real-World Dev Example**  
The denoising network inside Stable Diffusion is a U-Net: it takes a noisy latent + time-step + text embedding, and predicts the noise to remove.

**ASCII Diagram**
```
Input
 │
[Conv] → skip ─────────────────────┐
  │                                │
[Conv] → skip ──────────────┐      │
  │                         │      │
[Bottleneck]                │      │
  │                         │      │
[Upsample] ← skip───────────┘      │
  │                                │
[Upsample] ← skip───────────────────┘
  │
Output (same size as input)
```

### Gotchas & Dev Context
- **Skip connections** preserve fine spatial detail lost during downsampling — critical for sharp edges.
- Attention layers are injected into modern U-Nets (for text conditioning in diffusion).
- The bottleneck captures global context; skip connections restore local detail.
- Memory usage scales with input resolution — tile large images for segmentation.

### Production FAQ
**Q: Why is U-Net preferred over a plain encoder-decoder for segmentation?**  
A: Skip connections pass high-frequency spatial info directly to the decoder, recovering fine details that pure pooling destroys.

**Q: Can U-Net handle 3D medical volumes?**  
A: Yes — 3D U-Net replaces 2D convolutions with 3D convolutions and is standard for CT/MRI scan segmentation.

---

## 9. ControlNet

**Definition**  
An add-on to diffusion models that lets you control image generation using structural guides like edge maps, depth maps, poses, or sketches — while still following a text prompt.

**Real-World Dev Example**  
A product designer sketches a rough outline of a shoe, feeds it into ControlNet (Canny edge mode) with prompt "leather sneaker, product photo" — the model generates a photorealistic shoe matching the exact sketch proportions.

**ASCII Diagram**
```
Text Prompt ──────────────────┐
                              ▼
Control Signal (edge/pose) → ControlNet → U-Net → Generated Image
```

### Gotchas & Dev Context
- ControlNet is a **trainable copy of the U-Net encoder** — it does not replace SD's weights, just adds conditions.
- Common modes: **Canny** (edges), **Depth**, **OpenPose** (body pose), **Scribble**, **Seg** (segmentation mask).
- Can stack multiple ControlNets (e.g., depth + pose simultaneously) with weight blending.
- Higher control weight = more rigid adherence to the guide, less creative freedom.
- IP-Adapter is a lightweight alternative for style/reference image control.

### Production FAQ
**Q: My ControlNet output ignores the control image — why?**  
A: Control weight is likely too low (<0.5). Also confirm the preprocessor (e.g., Canny detector) matches the ControlNet model type.

**Q: Can I train my own ControlNet for a custom signal (e.g., floor plans)?**  
A: Yes — the official training script needs ~50K paired (control signal, image) examples and a single GPU week of training on an A100.

---

## 10. Image-to-Image / Inpainting / Outpainting

**Definition**  
- **Img2Img**: Transform an existing image using a prompt + noise level (strength).
- **Inpainting**: Fill in a masked (hidden) region of an image.
- **Outpainting**: Extend an image beyond its borders by generating new content.

**Real-World Dev Example**  
An e-commerce team inpaints product photos to remove messy backgrounds and replaces them with clean studio-white using a diffusion inpainting model — saving hours of manual Photoshop work.

### Gotchas & Dev Context
- **Denoising strength** (0–1): 0 = no change, 1 = ignore original, 0.5–0.75 is the sweet spot for img2img.
- Inpainting requires a **binary mask** (white = regenerate, black = keep).
- Outpainting works by padding the canvas and inpainting the new region with the original as context.
- Edge consistency is tricky — generated region must blend with original; use feathered masks.
- Specialised inpainting models (e.g., `sd-v1-5-inpainting`) outperform base models for this task.

### Production FAQ
**Q: Inpainted region looks "patchy" and doesn't match — fix?**  
A: Expand the mask slightly to include the border, use a feathered/blurred mask edge, and match the prompt to the existing image style.

**Q: Can I outpaint large areas reliably?**  
A: Incrementally — extend by 30–50% at a time, using the previous output as the new input. Large single jumps lose coherence.

---

## 11. OCR (Optical Character Recognition)

**Definition**  
Converting images of text (scanned docs, photos, screenshots) into machine-readable strings. Modern OCR uses deep learning to handle curved, handwritten, and multi-language text.

**Real-World Dev Example**  
A fintech startup uses PaddleOCR to extract invoice fields (vendor name, total amount, date) from uploaded PDF scans, auto-populating their accounting system.

**ASCII Diagram**
```
Image of text
  └─> Text Detection (find text regions)
        └─> Text Recognition (read each region)
               └─> "Invoice #4521  Total: $320.00"
```

### Gotchas & Dev Context
- **Two stages**: detect text bounding boxes → recognise characters in each box.
- Popular engines: **Tesseract** (open-source, older), **PaddleOCR** (fast, multi-language), **EasyOCR**, **Azure/Google Vision API**.
- Handwriting recognition (HTR) is much harder — needs specialised models.
- Poor image quality (blur, skew, noise) tanks accuracy — pre-process with deskewing and binarisation.
- Tables and complex layouts require post-processing to structure the extracted text.

### Production FAQ
**Q: Tesseract works in testing but fails on real scanned documents — why?**  
A: Real scans have noise, skew, and varying contrast. Pre-process with OpenCV: deskew, threshold (Otsu), denoise, then pass to Tesseract.

**Q: Which OCR handles non-Latin scripts (Arabic, Hindi) well?**  
A: PaddleOCR (80+ languages), EasyOCR, or cloud APIs (Google Vision, Azure Cognitive). Tesseract supports them but lags in accuracy.

---

## 12. Face Detection / Recognition

**Definition**  
- **Face Detection**: Find where faces are in an image (bounding boxes).
- **Face Recognition**: Identify *whose* face it is by comparing embeddings to a database.

**Real-World Dev Example**  
An attendance system uses RetinaFace to detect employees' faces from a lobby camera, then ArcFace embeddings to match against enrolled photos — clocking in without ID cards.

**ASCII Diagram**
```
Camera Frame
  └─> Face Detector (find boxes)
        └─> Face Alignment (normalise)
              └─> Embedding Model (128-d vector)
                    └─> Cosine similarity vs DB → "Alice (98%)"
```

### Gotchas & Dev Context
- Detection models: **MTCNN**, **RetinaFace**, **MediaPipe Face**.
- Recognition models: **ArcFace**, **FaceNet**, **DeepFace** (wrapper library).
- Match by **cosine similarity** or **Euclidean distance** on 128/512-d embeddings.
- Threshold tuning is critical: too low = false positives, too high = false negatives.
- Masks, glasses, extreme angles degrade accuracy significantly.
- ⚠️ **Ethics**: GDPR/CCPA require explicit consent for biometric data in most regions.

### Production FAQ
**Q: How do I add a new person without retraining?**  
A: Enrol them — extract their embedding(s) and add to the database. No retraining needed with embedding-based systems.

**Q: What's a good similarity threshold for 1:1 verification vs 1:N identification?**  
A: Verification: cosine sim > 0.6 is typical. Identification (1:N) needs a stricter threshold (0.7+) to avoid false matches in large DBs.

---

## 13. Pose Estimation

**Definition**  
Detecting and localising key body joints (shoulders, elbows, knees, etc.) in an image or video to understand body position and movement.

**Real-World Dev Example**  
A fitness app uses MediaPipe Pose to count push-up reps by tracking elbow angle in real-time from a phone camera — no wearables needed.

**ASCII Diagram**
```
Image
  └─> Pose Model
        └─> Keypoints: nose, l_shoulder, r_shoulder,
                       l_elbow, r_elbow, l_wrist, r_wrist ...
                             ↓
                      Skeleton drawn as lines
```

### Gotchas & Dev Context
- **2D pose**: keypoints as (x, y) pixel coordinates.
- **3D pose**: adds depth (z), needed for VR/biomechanics.
- Popular models: **OpenPose**, **MediaPipe Pose** (real-time, mobile-friendly), **ViTPose** (most accurate).
- Occlusion (one arm behind back) causes missed or "ghosted" keypoints.
- Multi-person pose: detect all persons first, then estimate pose per person (top-down), or predict all at once (bottom-up — faster).

### Production FAQ
**Q: Pose estimation is jittery in video — how to smooth it?**  
A: Apply a **Kalman filter** or simple temporal smoothing (moving average over 3–5 frames) to keypoint coordinates.

**Q: Can pose estimation work for animals or custom objects?**  
A: Yes — tools like **DeepLabCut** specialise in animal pose; you can also train custom keypoint detectors with labelled data.

---

## 14. Data Augmentation (Flip, Rotate, CutOut, MixUp)

**Definition**  
Artificially expanding your training dataset by applying random transformations to existing images — teaches the model to be robust to real-world variation without collecting more data.

**Real-World Dev Example**  
A medical X-ray classifier trains on only 2,000 images but uses flipping, rotation, and CutOut to effectively triple effective diversity, reducing overfitting.

### Gotchas & Dev Context
- **Flip** (horizontal/vertical): free augmentation, but vertical flip is wrong for tasks where orientation matters (e.g., text, driving).
- **Rotate**: add padding or crop to avoid black corners.
- **CutOut / Random Erasing**: masks a random rectangle to simulate occlusion. Forces the model not to rely on one region.
- **MixUp**: blends two images and their labels (e.g., 60% cat + 40% dog → soft label). Improves calibration.
- **CutMix**: cuts a patch from image B and pastes into image A with mixed labels.
- Libraries: `albumentations` (fast, flexible), `torchvision.transforms`, `imgaug`.
- Don't augment the validation set — it must reflect real distribution.

### Production FAQ
**Q: Is more augmentation always better?**  
A: No — excessive augmentation (e.g., heavy colour jitter on X-rays) can destroy diagnostically important features. Match augmentation to domain constraints.

**Q: Should I augment bounding box labels during object detection training?**  
A: Yes — any geometric transform (flip, rotate, crop) must also transform the box coordinates. `albumentations` handles this automatically.

---

## 15. Transfer Learning (ImageNet Pretrained)

**Definition**  
Reusing a model pretrained on a large dataset (e.g., ImageNet's 1.2M images, 1000 classes) as a starting point for your own task — you're borrowing learned visual features instead of starting from scratch.

**Real-World Dev Example**  
A startup building a skin lesion classifier fine-tunes a ResNet-50 pretrained on ImageNet using just 3,000 labelled dermatology images — reaching 89% accuracy in hours, not weeks.

**ASCII Diagram**
```
ImageNet Pretrained ResNet-50
  ├── Conv layers (frozen) ← general features: edges, textures, shapes
  └── Final FC layer (replaced) ← your custom classes
```

### Gotchas & Dev Context
- **Feature extraction**: freeze all pretrained layers, only train the new head.
- **Fine-tuning**: unfreeze top layers too, use a smaller learning rate (1e-4 to 1e-5).
- The more different your data is from ImageNet, the deeper you should fine-tune.
- ImageNet features generalise surprisingly well even to non-photographic domains (histology, satellite imagery).
- Use `torchvision.models` or `timm` library for pretrained models.

### Production FAQ
**Q: Should I always freeze the backbone first?**  
A: Train the head-only for a few epochs first (stabilises the new head), then unfreeze and fine-tune with a lower LR. Unfreezing all at once can destroy pretrained weights.

**Q: My dataset is very different from ImageNet (e.g., satellite imagery) — does transfer still help?**  
A: Usually yes — low-level features (edges, colours, textures) are universal. But you may need to fine-tune more layers and use a lower learning rate.

---

## 16. Vision Transformer (ViT)

**Definition**  
A Transformer architecture (originally from NLP) applied to images by splitting an image into fixed-size patches and treating each patch as a "token" — no convolutions required.

**Real-World Dev Example**  
Google's ViT-L/16 is deployed in image search: it encodes query images as patch embeddings and retrieves visually similar results from a billion-image index.

**ASCII Diagram**
```
Image (224×224)
  └─> Split into 16×16 patches (196 patches)
        └─> Linear embed each patch → sequence of tokens
              └─> + Position embedding
                    └─> Transformer Encoder (self-attention)
                          └─> [CLS] token → Classification head
```

### Gotchas & Dev Context
- ViT needs **large datasets** to outperform CNNs — underperforms on small data without pretrained weights.
- **DeiT** adds knowledge distillation to train ViT efficiently on smaller datasets.
- Self-attention is **O(n²)** in patch count — high-res images are expensive; use **Swin Transformer** (window attention) instead.
- Position embeddings matter — without them, ViT is permutation-invariant (bad for images).
- `timm` library has 500+ pretrained ViT variants.

### Production FAQ
**Q: ViT vs ResNet — which for production image classification?**  
A: For large datasets and highest accuracy: ViT/Swin. For small datasets or edge devices: ResNet or EfficientNet. ViT has higher compute costs.

**Q: Why does ViT need such a large dataset to train from scratch?**  
A: CNNs have built-in inductive biases (locality, translation invariance) that help with small data. ViT must *learn* these from data, requiring millions of examples.

---

## 17. CLIP (Contrastive Language-Image Pre-training)

**Definition**  
OpenAI's model trained to align image and text embeddings — it learns that a photo of a dog and the text "a dog playing fetch" should be close in shared embedding space.

**Real-World Dev Example**  
A stock photo site uses CLIP to power natural-language search: user types "cosy coffee shop in autumn" — CLIP ranks 10M images by embedding similarity to the query, no manual tags needed.

**ASCII Diagram**
```
"a dog playing fetch"  → [Text Encoder]  → text_embedding
[Photo of dog]         → [Image Encoder] → image_embedding

Cosine similarity(text_embedding, image_embedding) → high score ✓
```

### Gotchas & Dev Context
- CLIP is a **zero-shot** model — use it without any task-specific fine-tuning.
- Zero-shot classification: embed all class names as text, embed the image, pick the closest class text.
- Works poorly on fine-grained tasks (e.g., distinguishing dog breeds) — fine-tune with your domain data.
- Sensitive to prompt wording: `"a photo of a {class}"` often outperforms just `"{class}"`.
- Basis for DALL·E, Stable Diffusion guidance, and many retrieval systems.

### Production FAQ
**Q: How do I use CLIP for image search at scale?**  
A: Pre-compute image embeddings offline, store in a vector DB (FAISS, Pinecone, Weaviate), then at query time embed the text and run ANN search.

**Q: CLIP gets confused between similar categories — fix?**  
A: Use **prompt ensembling** (average embeddings of multiple prompts: "a photo of {c}", "an image of {c}", etc.) — it consistently improves accuracy by 3–5%.

---

## 18. Multimodal Models (GPT-4V, LLaVA, Gemini)

**Definition**  
AI models that can process and reason over multiple input types — typically text and images together — enabling tasks like visual question answering, image captioning, and document understanding.

**Real-World Dev Example**  
A retail company sends product photos + "list all defects visible" to GPT-4V via the vision API — it returns structured defect descriptions, replacing a manual QA checklist.

**ASCII Diagram**
```
[Image] → Vision Encoder (e.g., CLIP ViT)
                │
                ▼
         Visual Tokens ──┐
                          ├──> LLM (GPT-4 / LLaMA) → Text Response
Text Prompt Tokens ───────┘
```

### Gotchas & Dev Context
- **GPT-4V / GPT-4o**: Best reasoning, closed API, charged per token (images cost ~800–1500 tokens).
- **LLaVA**: Open-source, runs locally, based on LLaMA. Great for private/offline use.
- **Gemini 1.5 Pro**: Supports very long contexts, handles multiple images + video frames.
- Vision encoders (usually CLIP-based) compress images to visual tokens — fine detail may be lost.
- Not reliable for pixel-perfect tasks (exact OCR, precise measurements) — still hallucinate.
- **Grounding**: models describe *what's there* but don't always know *where* (no bounding boxes by default).

### Production FAQ
**Q: GPT-4V sometimes "hallucinates" image content — how to reduce this?**  
A: Ask the model to say "I don't know" when unsure, use structured output with JSON mode, and validate against separate deterministic OCR/detection pipelines for critical fields.

**Q: LLaVA vs GPT-4V — when to pick open-source?**  
A: LLaVA for cost-sensitive, privacy-requiring, or offline deployments. GPT-4V for maximum reasoning quality when cost and data egress are acceptable.

---

*End of Batch 8 — Computer Vision*
