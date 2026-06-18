# Batch 1 — AI Fundamentals
> Core concepts every AI/ML developer must know before anything else.

---

## 1. Artificial Intelligence (AI)

### Definition
AI is the broad field of building systems that can perform tasks which normally require human intelligence — reasoning, understanding language, recognizing images, making decisions.

### Real-World Dev Example
A spam filter that decides whether your email is junk or not is an AI system. You don't hard-code rules; you build something that *learns* what spam looks like.

### ASCII Diagram
```
  Human Task                AI System
  ─────────────────────────────────────
  "Is this email spam?"  →  [Model] → Yes / No
  "What's in this photo?" → [Model] → "cat"
  "Translate this text"  →  [Model] → "Hola"
```

### Gotchas & Dev Context
- AI is the **umbrella term**. ML and DL are subsets of it.
- "AI" in marketing often means a simple rule-based system. Real AI learns from data.
- Not all AI is ML — expert systems (hand-coded rules) are AI too, just older-style.
- AI ≠ sentience or consciousness. It's pattern matching at scale.

### Production FAQ
**Q: Is every AI system a black box?**
A: No. Rule-based AI is fully transparent. Neural networks are harder to interpret, which is why the explainability (XAI) field exists.

**Q: When should I use AI vs. a traditional algorithm?**
A: Use AI when the rules are too complex or numerous to write by hand (e.g., face recognition). Use traditional algorithms when the problem is well-defined and deterministic (e.g., sorting).

**Q: What's the difference between "AI" and "automation"?**
A: Automation follows fixed rules. AI adapts — it handles inputs it hasn't seen explicitly before.

---

## 2. Machine Learning (ML)

### Definition
ML is a subset of AI where systems learn patterns from data without being explicitly programmed with rules. The program *improves* with experience.

### Real-World Dev Example
Training a model on thousands of house prices (size, location, age) so it can predict the price of a new house it has never seen — no hand-coded pricing formula needed.

### ASCII Diagram
```
Traditional Programming:
  Rules + Data → Output

Machine Learning:
  Data + Output → Rules (the learned model)
```

### Gotchas & Dev Context
- ML does **not** guarantee correct answers — it gives statistically likely answers.
- More data is usually more powerful than a fancier algorithm.
- "Garbage in, garbage out" — bad training data produces bad models.
- ML requires careful evaluation; a model that scores 95% accuracy might still fail badly on edge cases.

### Production FAQ
**Q: How much data do I need to start?**
A: It depends on the problem. Simple tabular tasks may work with thousands of rows. Image/NLP tasks often need millions. Start with what you have and benchmark.

**Q: Is ML always better than classical statistics?**
A: No. If your data is small and interpretability matters (e.g., medical decisions), logistic regression or decision trees often outperform black-box ML.

**Q: Can ML models become outdated?**
A: Yes — this is called **model drift**. If the real-world data distribution changes (e.g., user behavior shifts), the model's predictions degrade and it needs retraining.

---

## 3. Deep Learning (DL)

### Definition
DL is a subset of ML that uses artificial neural networks with many layers (hence "deep") to learn complex patterns directly from raw data like images, audio, or text.

### Real-World Dev Example
GPT, image classifiers (ResNet), and speech-to-text (Whisper) are all deep learning models. They automatically learn features like edges, shapes, or word meanings from raw input.

### ASCII Diagram
```
Input Layer    Hidden Layers (many)    Output Layer
  [x1]  →  [●]─[●]─[●]─[●]─[●]  →  [Prediction]
  [x2]  →  [●]─[●]─[●]─[●]─[●]
  [x3]  →  [●]─[●]─[●]─[●]─[●]
         (each ● is a neuron)
```

### Gotchas & Dev Context
- DL needs **lots of data and compute** (GPUs/TPUs). Don't default to DL for small datasets.
- DL models are usually harder to interpret than classical ML models.
- Transfer learning lets you reuse pre-trained DL models, dramatically reducing data requirements.
- DL ⊂ ML ⊂ AI. All deep learning is ML, but not all ML is deep learning.

### Production FAQ
**Q: When should I use DL vs. classical ML?**
A: Use DL for unstructured data (images, audio, text). For structured tabular data, gradient boosted trees (XGBoost, LightGBM) often match or beat DL with far less cost.

**Q: Why does DL need GPUs?**
A: Neural networks involve billions of floating-point multiplications done in parallel. GPUs are architected for exactly that type of massively parallel math.

**Q: Is PyTorch or TensorFlow better?**
A: PyTorch dominates research; TensorFlow/Keras is strong in production deployment. Both are fine — pick whichever your team knows.

---

## 4. Supervised Learning

### Definition
A type of ML where the model learns from **labeled** data — each input example has a correct answer attached — and learns to map inputs to outputs.

### Real-World Dev Example
Training an email classifier with thousands of emails already labeled `spam` or `not spam`. The model learns the mapping and can classify new, unlabeled emails.

### ASCII Diagram
```
Training Data:
  Email_1 → "spam"
  Email_2 → "not spam"
  Email_3 → "spam"
       ↓
  [Model learns mapping]
       ↓
New Email → Model → "spam" ✓
```

### Gotchas & Dev Context
- Labeling data is expensive and time-consuming — this is often the hardest part in practice.
- If labels are noisy (wrong), model quality degrades badly.
- Two main tasks: **Classification** (discrete output: cat/dog) and **Regression** (continuous output: house price).
- Watch out for **class imbalance** — 99% negative class means a dumb model can hit 99% accuracy by guessing negative every time.

### Production FAQ
**Q: How do I get labeled data cheaply?**
A: Use crowdsourcing (Amazon Mechanical Turk), weak supervision (Snorkel), or active learning to label only the most informative examples first.

**Q: What's the difference between multi-class and multi-label classification?**
A: Multi-class: each sample belongs to exactly one class (cat vs. dog vs. bird). Multi-label: a sample can belong to multiple classes simultaneously (a photo tagged with both "beach" and "sunset").

**Q: Can supervised learning fail even with perfect labels?**
A: Yes — if the features don't contain enough signal to predict the output, no algorithm will help. Feature engineering and domain knowledge matter.

---

## 5. Unsupervised Learning

### Definition
A type of ML where the model learns from **unlabeled** data, discovering hidden patterns, structure, or groupings on its own.

### Real-World Dev Example
Clustering a million customer records by purchasing behavior to discover natural customer segments — without any pre-defined category labels.

### ASCII Diagram
```
Raw Data (no labels):            After Clustering:
  ●  ●    ◆  ◆                   [Group A] ●●●
  ●    ●  ◆    ◆    →            [Group B] ◆◆◆
  ●  ●    ◆  ◆                   [Group C] ▲▲▲
  ▲  ▲  ▲
```

### Gotchas & Dev Context
- You can't directly measure accuracy — there's no "right answer" to compare against.
- Common tasks: **Clustering** (K-Means, DBSCAN), **Dimensionality Reduction** (PCA, t-SNE, UMAP), **Anomaly Detection**.
- Results are subjective — "good" clusters require domain expertise to validate.
- Unsupervised pre-training is a key building block for self-supervised learning.

### Production FAQ
**Q: How do I evaluate unsupervised model quality?**
A: Use intrinsic metrics (silhouette score, inertia for clustering) or validate business impact (do the discovered segments make business sense?).

**Q: Is anomaly detection supervised or unsupervised?**
A: Usually unsupervised — you train on "normal" data and flag deviations. It can also be semi-supervised if you have a few labeled anomaly examples.

**Q: When does unsupervised learning beat supervised?**
A: When labeled data is scarce or impossible to obtain, or for exploratory analysis where you don't know the categories in advance.

---

## 6. Semi-Supervised Learning

### Definition
A hybrid approach that trains on a **small amount of labeled data** combined with a **large amount of unlabeled data**, getting much of the benefit of full supervision at lower labeling cost.

### Real-World Dev Example
You have 500 labeled medical images and 50,000 unlabeled ones. Semi-supervised learning uses all 50,500 to build a model far better than using only the 500 labeled ones.

### ASCII Diagram
```
  Labeled Data (small):     [img → "tumor"] × 500
  Unlabeled Data (large):   [img → ???    ] × 50,000
           ↓
  Semi-Supervised Model → Better than 500-label-only baseline
```

### Gotchas & Dev Context
- Assumes unlabeled data has the same distribution as labeled — violated distribution causes harm, not help.
- Common methods: **pseudo-labeling** (use model predictions as labels iteratively), **consistency regularization**, **label propagation**.
- Popular in NLP (pre-train on unlabeled text, fine-tune on small labeled set).
- Can backfire if the model's pseudo-labels are systematically wrong early in training.

### Production FAQ
**Q: How is semi-supervised different from pre-training + fine-tuning?**
A: Pre-training/fine-tuning (e.g., BERT) is a specific form of semi-supervised learning — unsupervised pre-training gives the model general knowledge, then labeled data fine-tunes it.

**Q: How much labeled data do I need for semi-supervised to help?**
A: Even 1–10% labeled data can yield strong results. The key is that the unlabeled data is plentiful and from the same domain.

**Q: Is it worth the complexity?**
A: Yes when labeling is the bottleneck. If you can label cheaply, just do full supervised learning — it's simpler and more predictable.

---

## 7. Self-Supervised Learning

### Definition
A learning paradigm where the model creates its **own supervision signal from the raw data** — it learns by solving cleverly designed pretext tasks that require no human labels.

### Real-World Dev Example
BERT is trained by randomly masking words in text and predicting the missing word. The "label" is the original word — extracted automatically, no human needed.

### ASCII Diagram
```
Raw text: "The cat sat on the [MASK]"
                                 ↓
              Model predicts: "mat"   ← self-generated label
```

### Gotchas & Dev Context
- The pretext task must be hard enough to force learning useful representations (not trivially solvable).
- Powers most modern foundation models: BERT, GPT, CLIP, MAE, SimCLR.
- The key insight: raw data is the label — this unlocks *internet-scale* training without annotation.
- Different from unsupervised: SSL has a defined predictive loss; unsupervised has no explicit target.

### Production FAQ
**Q: When should I use self-supervised over supervised?**
A: When you have massive unlabeled data but few labeled examples. Self-supervised pre-training extracts rich representations; then fine-tune on your small labeled set.

**Q: What's a "pretext task"?**
A: An artificially constructed prediction task that forces the model to understand data structure — e.g., predict rotation angle of an image, predict the next token, reconstruct a masked patch.

**Q: Does self-supervised learning replace supervised learning?**
A: No — it precedes it. You still need labeled data for your final downstream task (e.g., sentiment classification), just far less of it.

---

## 8. Reinforcement Learning

### Definition
A learning paradigm where an **agent** learns to make decisions by taking actions in an environment, receiving **rewards** or **penalties**, and maximizing cumulative reward over time.

### Real-World Dev Example
Training a game-playing AI (AlphaGo, OpenAI Five) where the agent plays millions of games, receives +1 for winning and -1 for losing, and gradually learns winning strategies.

### ASCII Diagram
```
         Action
  Agent ──────→ Environment
    ↑                │
    └── Reward + State ←┘

Reward shaping:
  Win  → +1.0
  Draw →  0.0
  Lose → -1.0
```

### Gotchas & Dev Context
- RL is notoriously **sample-inefficient** — may need millions of steps to learn a simple task.
- **Reward hacking**: agent finds unintended shortcuts to maximize reward (e.g., spinning in circles scores points).
- Real-world RL is hard — you can't always reset the environment safely (robots, medical decisions).
- RLHF (RL from Human Feedback) is how ChatGPT-style models are fine-tuned to follow instructions.

### Production FAQ
**Q: Should I use RL for my recommendation system?**
A: Carefully. Contextual bandits (a lighter RL variant) are more practical for recommendations. Full RL is often overkill and unstable.

**Q: How is RL different from supervised learning?**
A: In SL, you have a correct answer for every input. In RL, you only get a delayed reward after a sequence of actions — you must figure out *which* actions caused the outcome.

**Q: What frameworks exist for RL?**
A: Stable Baselines3 (PyTorch), RLlib (Ray), Gymnasium (environments). For LLM fine-tuning: TRL (HuggingFace).

---

## 9. Training vs. Inference

### Definition
**Training** is the process of teaching a model by adjusting its parameters on data. **Inference** is using the trained model to make predictions on new inputs.

### Real-World Dev Example
- **Training**: Running your image classifier on 1M photos over 50 epochs on 8 GPUs for 12 hours.
- **Inference**: A user uploads a photo; your deployed model returns "golden retriever" in 20ms.

### ASCII Diagram
```
TRAINING (offline, expensive):
  Data → Model (updates weights) → Repeat → Trained Model

INFERENCE (online, fast):
  New Input → Trained Model (weights frozen) → Prediction
```

### Gotchas & Dev Context
- Training is **compute-heavy** (GPUs, days/weeks). Inference needs to be **fast and cheap** (latency SLAs).
- Optimize differently: training optimizes for accuracy; inference optimizes for speed/cost (quantization, distillation, batching).
- **Online inference**: single prediction per request. **Batch inference**: thousands of predictions queued and processed together.
- Model weights are **read-only** during inference — never modified.

### Production FAQ
**Q: Can I do inference on CPU?**
A: Yes, especially with quantized models. Small models (< 1B params) often run fine on CPU for latency-tolerant workloads.

**Q: What is "inference cost" and why does it matter?**
A: Every API call to a deployed model costs compute. At scale (millions of requests/day), inference cost often dwarfs training cost. Optimizing model size and batching is critical.

**Q: What's "real-time" vs "batch" inference in practice?**
A: Real-time: user-facing predictions (< 100ms). Batch: pre-computing recommendations overnight for millions of users without a latency constraint.

---

## 10. Model

### Definition
A model is the **learned mathematical function** that maps inputs to outputs after training — it encodes all the patterns the algorithm extracted from data.

### Real-World Dev Example
A trained BERT model is a file (~400MB) containing 110 million parameters. Load it, feed it a sentence, and it outputs a vector representing the sentence's meaning.

### ASCII Diagram
```
Input (features) → [Model: f(x)] → Output (prediction)

The model IS the function f — parameterized by weights W learned during training.
```

### Gotchas & Dev Context
- "Model" can refer to the **architecture** (ResNet-50) or the **trained artifact** (ResNet-50 trained on ImageNet). These are different things.
- Models are serialized to disk: `.pt` (PyTorch), `.h5`/`.keras` (Keras), `.onnx` (cross-framework), `.pkl` (scikit-learn).
- A model without its **training data distribution** context is dangerous to deploy blindly.
- Model versioning matters in production — track which model version made which prediction.

### Production FAQ
**Q: What's the difference between a model and an algorithm?**
A: The algorithm is the learning procedure (e.g., gradient descent + backprop). The model is the *result* after running that algorithm on data — the trained weights.

**Q: How do I serve a model in production?**
A: Common options: Flask/FastAPI (custom), TorchServe, TF Serving, Triton Inference Server, or managed endpoints (AWS SageMaker, GCP Vertex AI, Azure ML).

**Q: How large can production models get?**
A: From kilobytes (linear regression) to hundreds of gigabytes (LLaMA 70B). Model compression (quantization, pruning, distillation) is essential for large model deployment.

---

## 11. Features & Labels

### Definition
**Features** are the input variables the model uses to make predictions. **Labels** are the target outputs the model is trained to predict in supervised learning.

### Real-World Dev Example
Predicting house price:
- Features: `[square_feet=1500, bedrooms=3, location="NYC", age=10]`
- Label: `$850,000`

### ASCII Diagram
```
  Feature Matrix (X)          Labels (y)
  ┌─────┬──────┬──────┐       ┌─────────┐
  │ sqft│ beds │ loc  │       │  price  │
  ├─────┼──────┼──────┤       ├─────────┤
  │1500 │  3   │ NYC  │  →    │ 850,000 │
  │ 900 │  2   │ LA   │  →    │ 620,000 │
  └─────┴──────┴──────┘       └─────────┘
```

### Gotchas & Dev Context
- **Feature engineering** — creating good features — often matters more than algorithm choice.
- Avoid **data leakage**: don't include features that wouldn't be available at inference time (e.g., future data).
- **Feature scaling** matters for many algorithms (SVM, neural nets). Tree-based models are scale-invariant.
- High-cardinality categorical features (millions of unique IDs) need careful encoding.

### Production FAQ
**Q: What's feature importance and why does it matter?**
A: Feature importance ranks which inputs most influence predictions. Useful for debugging, removing useless features, and understanding model behavior.

**Q: What happens if a feature is missing at inference time?**
A: The model may error or silently produce bad predictions. Always handle missing values explicitly in your inference pipeline.

**Q: What's the difference between raw features and engineered features?**
A: Raw: direct from data (`timestamp`). Engineered: derived signal (`day_of_week`, `is_weekend`, `hour`). Good feature engineering often unlocks model performance.

---

## 12. Dataset (Training, Validation, Test)

### Definition
A dataset is a collection of examples used to train, tune, or evaluate a model. It is split into three non-overlapping sets: **training**, **validation**, and **test**.

### Real-World Dev Example
You have 100,000 images. You split: 70K for training, 15K for validation (tuning hyperparameters), 15K for the final test (one-time honest evaluation).

### ASCII Diagram
```
Full Dataset (100%)
├── Training Set   (~70%) ← Model learns here
├── Validation Set (~15%) ← Tune hyperparameters, detect overfitting
└── Test Set       (~15%) ← Final, one-time evaluation (DO NOT PEEK EARLY)
```

### Gotchas & Dev Context
- **Never tune on test set** — you'll get optimistically biased results that won't hold in production.
- If you peek at test set performance to make decisions, it becomes a second validation set.
- For small datasets, use **cross-validation** instead of a static split.
- Time-series data must be split **chronologically** — random splits cause data leakage.

### Production FAQ
**Q: What split ratio should I use?**
A: No universal rule. 70/15/15 or 80/10/10 are common. With very large datasets (millions), even 1% for validation/test is often enough.

**Q: Can validation and test sets be the same?**
A: No — this is a common mistake. Validation is for iterative tuning (touched many times); test is for final unbiased evaluation (touched once).

**Q: What if my dataset is too small to split 3 ways?**
A: Use k-fold cross-validation to estimate generalization, and hold out a small test set. Or use nested cross-validation.

---

## 13. Overfitting & Underfitting

### Definition
**Overfitting**: the model memorizes training data but fails on new data (too complex). **Underfitting**: the model is too simple to capture patterns even in training data.

### Real-World Dev Example
- Overfit: A decision tree with 1000 leaves memorizes every training record — 100% train accuracy, 60% test accuracy.
- Underfit: A linear model predicting housing prices in a highly non-linear market — bad on both train and test.

### ASCII Diagram
```
  Error
    │    Underfit  │  Good fit  │  Overfit
    │    ╲         │            │         ╱  ← train error
    │     ╲        │   ──────   │        ╱
    │      ╲       │            │  ╱╲   ╱   ← val error
    │       ╲──────┤            ├──  ───
    └────────────────────────────────── Model Complexity
```

### Gotchas & Dev Context
- Signs of overfitting: training loss keeps falling, validation loss starts rising.
- Fixes for overfitting: more data, dropout, regularization (L1/L2), early stopping, simpler model.
- Fixes for underfitting: more features, more model capacity, longer training, better feature engineering.
- A model that's slightly overfit to train set is normal and often acceptable.

### Production FAQ
**Q: How do I detect overfitting in practice?**
A: Monitor both train and validation loss curves side by side during training. Divergence = overfitting.

**Q: Does more data always fix overfitting?**
A: Yes, data is the most reliable cure. Regularization techniques are second-best substitutes when data is scarce.

**Q: What is "early stopping"?**
A: Stop training when validation loss stops improving (save the checkpoint from the best validation epoch). Simple, effective, and commonly used.

---

## 14. Bias-Variance Tradeoff

### Definition
**Bias** is error from wrong assumptions (model too simple). **Variance** is error from sensitivity to training data fluctuations (model too complex). Reducing one tends to increase the other.

### Real-World Dev Example
A linear model predicting a curved relationship has high bias. A 20-layer neural net trained on 100 samples has high variance — tiny data changes flip its predictions.

### ASCII Diagram
```
           Bias      Variance    Total Error
Simple  →  High   +   Low     =   High
Complex →  Low    +   High    =   High
SWEET SPOT: balance both → lowest total error
```

### Gotchas & Dev Context
- This tradeoff is conceptual — modern deep learning challenges it (double descent phenomenon: very large models can have both low bias AND low variance).
- Ensemble methods (bagging, boosting) help manage this tradeoff.
- **Bagging** (Random Forest) reduces variance. **Boosting** (XGBoost) reduces bias.
- In practice: start simple (high bias), add complexity only when you have evidence it helps.

### Production FAQ
**Q: How does regularization relate to bias-variance?**
A: Regularization increases bias (adds assumptions) to reduce variance. It's a deliberate tradeoff that improves generalization when data is limited.

**Q: Is high variance always bad?**
A: In a single model, yes. But ensembling many high-variance models (bagging) averages out their errors, yielding a robust result.

**Q: What's the "double descent" phenomenon?**
A: In very large models (overparameterized), test error can rise then fall again as model size grows — surprising because classical theory predicts it should only rise after a point.

---

## 15. Cross-Validation

### Definition
A technique to estimate model generalization by training and evaluating the model on **multiple different splits** of the same dataset, rotating which portion is held out each time.

### Real-World Dev Example
With 1,000 samples and 5-fold CV: split into 5 groups of 200. Train on 4 groups, evaluate on the 5th. Repeat 5 times rotating the held-out group. Average the 5 scores.

### ASCII Diagram
```
Fold 1: [VAL][TRN][TRN][TRN][TRN] → score_1
Fold 2: [TRN][VAL][TRN][TRN][TRN] → score_2
Fold 3: [TRN][TRN][VAL][TRN][TRN] → score_3
Fold 4: [TRN][TRN][TRN][VAL][TRN] → score_4
Fold 5: [TRN][TRN][TRN][TRN][VAL] → score_5
Final Score = mean(score_1..5) ± std
```

### Gotchas & Dev Context
- Use CV when your dataset is too small for a reliable static validation split.
- **Stratified k-fold** preserves class distribution in each fold — always use for classification.
- **Never include test set in cross-validation** — it's still sacred for final evaluation.
- For time-series: use **TimeSeriesSplit** (forward chaining) — no random shuffling.

### Production FAQ
**Q: What k should I pick?**
A: k=5 or k=10 are standard. Higher k = lower bias, higher variance, more compute. k=N (leave-one-out) is useful only for very small datasets.

**Q: Should I use CV in production training?**
A: Use CV for model selection and hyperparameter tuning. Train the final model on the **full dataset** (train + validation combined) before deploying.

**Q: Does CV replace a test set?**
A: No — CV estimates performance on training data splits. A held-out test set gives a final unbiased estimate on completely unseen data.

---

## 16. Hyperparameters vs. Parameters

### Definition
**Parameters** are values the model *learns* from data during training (e.g., weights). **Hyperparameters** are values you *set manually* before training that control how training happens.

### Real-World Dev Example
In a neural network:
- **Parameters**: the millions of weight values (W, b) — learned via gradient descent.
- **Hyperparameters**: learning rate, number of layers, batch size, dropout rate — set by you.

### ASCII Diagram
```
You set:            Model learns:
  learning_rate   →   weight_1 = 0.342
  num_layers      →   weight_2 = -1.17
  batch_size      →   bias_1   = 0.005
  dropout         →   ...millions more
```

### Gotchas & Dev Context
- Hyperparameter tuning is expensive — each config requires a full training run to evaluate.
- Common tuning strategies: **Grid Search** (exhaustive), **Random Search** (often better), **Bayesian Optimization** (smarter, uses previous results).
- Tools: Optuna, Ray Tune, Weights & Biases Sweeps.
- A model's **architecture** choices (number of neurons, layer types) are also hyperparameters.

### Production FAQ
**Q: How many hyperparameters should I tune at once?**
A: Focus on the highest-impact ones first: learning rate, batch size, model size. Random search across 20–50 trials usually finds a good region.

**Q: Are hyperparameters fixed after deployment?**
A: Yes — hyperparameters define the model structure. When you retrain (e.g., on new data), you can use the same tuned hyperparameters unless distribution shifts significantly.

**Q: What's AutoML?**
A: Automated machine learning — tools (AutoKeras, H2O AutoML, Google AutoML) that automate hyperparameter search, architecture selection, and sometimes feature engineering.

---

## 17. Epoch, Batch, Iteration

### Definition
- **Epoch**: one full pass through the entire training dataset.
- **Batch**: a subset of training data processed together in one forward/backward pass.
- **Iteration**: one forward + backward pass on a single batch.

### Real-World Dev Example
Dataset: 10,000 samples. Batch size: 100. → 100 iterations per epoch. Running for 50 epochs = 5,000 total iterations.

### ASCII Diagram
```
Dataset: [S1 S2 S3 ... S10000]

Epoch 1:
  Iter 1: [S1...S100]   → forward → loss → backward → update weights
  Iter 2: [S101...S200] → forward → loss → backward → update weights
  ...
  Iter 100: [S9901...S10000] ← end of epoch 1

Epoch 2: shuffle + repeat
```

### Gotchas & Dev Context
- **Larger batch** = faster training but uses more GPU memory; may hurt generalization.
- **Smaller batch** = noisier gradients, acts as implicit regularization, often generalizes better.
- Training loss is typically logged per iteration; validation metrics per epoch.
- Gradient accumulation lets you simulate large batches on limited GPU memory.

### Production FAQ
**Q: How many epochs should I train for?**
A: Use early stopping — train until validation loss stops improving. There's no universal fixed number.

**Q: Why shuffle data between epochs?**
A: To prevent the model from memorizing the order of samples, which can cause optimization instability and bias.

**Q: What batch size should I use?**
A: Start with 32 or 64. Scale up if GPU memory allows. Some research suggests batch size 256–2048 with a proportionally scaled learning rate for large-scale training.

---

## 18. Learning Rate

### Definition
The learning rate (lr) controls **how large a step** the optimizer takes when updating model weights — the most important hyperparameter in neural network training.

### Real-World Dev Example
If lr is too high, training diverges (loss explodes). If too low, training is painfully slow or gets stuck. A typical starting point for Adam is `lr=1e-3`.

### ASCII Diagram
```
Loss Surface:
          ╲          ╱
           ╲        ╱
            ╲      ╱
 Too high lr: ⟵ bounces over minimum
 Too low lr:  ⟶ creeps very slowly
 Just right:  ⟶ converges to ●minimum

```

### Gotchas & Dev Context
- **Learning rate schedule**: start high, decay over time (step decay, cosine annealing, warmup + decay).
- **Warmup**: slowly ramp up lr at the start of training to stabilize early gradient updates (standard for Transformers).
- LR is often the first thing to tune when training is unstable.
- **LR Finder** (fast.ai technique): increase lr exponentially and plot loss — pick lr just before loss spikes.

### Production FAQ
**Q: Should I use the same lr throughout training?**
A: Usually no. LR scheduling (decay over epochs) almost always improves final performance. Cosine annealing and OneCycleLR are popular choices.

**Q: What's a "learning rate warmup"?**
A: Gradually increasing lr from near-zero for the first N steps. Critical for large Transformer models to prevent early training instability.

**Q: What if my loss oscillates wildly?**
A: Lower your learning rate. Also check for: bad data normalization, exploding gradients (add gradient clipping), or too large a batch size.

---

## 19. Loss Function

### Definition
A loss function measures **how wrong the model's predictions are** compared to the true labels. Training minimizes this value by adjusting model weights.

### Real-World Dev Example
Predicting house prices? Use **Mean Squared Error (MSE)** — it penalizes large errors heavily. Classifying emails as spam/not-spam? Use **Binary Cross-Entropy** — designed for probability outputs.

### ASCII Diagram
```
Prediction: 0.9  |  True Label: 1.0
                 |
BCE Loss = -[1.0 * log(0.9)] = 0.105  ← small, prediction close to truth
BCE Loss = -[1.0 * log(0.1)] = 2.302  ← large, prediction very wrong

Minimize this value over all training examples → model improves
```

### Gotchas & Dev Context
- **MSE** (regression): sensitive to outliers. Use **MAE** or **Huber loss** for robust regression.
- **Cross-Entropy** (classification): standard for categorical predictions. Use **Focal Loss** for severe class imbalance.
- A decreasing training loss ≠ better model. Watch **validation loss**, not just training loss.
- Loss and evaluation metrics are different: you optimize loss; you report accuracy/F1/AUC.

### Production FAQ
**Q: Why not just use accuracy as the loss function?**
A: Accuracy is not differentiable (can't compute gradients). Loss functions must be smooth and differentiable for gradient descent to work.

**Q: What happens if I pick the wrong loss function?**
A: Training may converge to a suboptimal solution. E.g., using MSE for classification works but is much slower/weaker than cross-entropy.

**Q: Can I use multiple loss functions?**
A: Yes — combined losses are common. E.g., `total_loss = classification_loss + λ * reconstruction_loss`. The weight λ controls the tradeoff.

---

## 20. Gradient Descent (SGD, Adam, AdamW)

### Definition
Gradient descent is the core **optimization algorithm** that adjusts model weights by computing the gradient of the loss and stepping in the direction that reduces it.

### Real-World Dev Example
Your model predicts 0.3 for a sample labeled 1.0. The loss is high. Gradient descent computes "which direction should each weight change to lower this loss?" and nudges them accordingly.

### ASCII Diagram
```
Loss
  │  ╲
  │   ╲              Gradient = slope at current point
  │    ╲   ●         Step = -gradient × learning_rate
  │     ╲ ↗
  │      ●           Repeat until reaching minimum ●
  │       ╲         ╱
  │        ╲       ╱
  │         ●─────●  ← minimum
  └──────────────────── Weights
```

### Variants

| Optimizer | Key Trait | Best For |
|-----------|-----------|----------|
| **SGD** | Simple, noisy updates; momentum variant common | CV tasks, when you can tune carefully |
| **Adam** | Adaptive per-weight learning rates; fast convergence | NLP, default choice for most tasks |
| **AdamW** | Adam + fixed weight decay (decoupled); better generalization | Transformers, LLMs — the modern standard |

### Gotchas & Dev Context
- **SGD + momentum** often beats Adam on final accuracy for vision models, but is harder to tune.
- **Adam** converges fast but can overfit — weight decay helps.
- **AdamW** decouples weight decay from gradient update — use this over vanilla Adam for Transformers.
- Gradient **clipping** prevents exploding gradients: `torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)`.

### Production FAQ
**Q: What optimizer should I default to?**
A: AdamW with a learning rate schedule for most tasks. SGD with momentum for ResNet-style CV models if you want peak accuracy with careful tuning.

**Q: What is "momentum" in SGD?**
A: A running average of past gradients that smooths updates and helps escape shallow local minima — analogous to a ball rolling downhill with inertia.

**Q: What's the difference between GD, SGD, and mini-batch GD?**
A: Full GD uses the whole dataset per step (slow, stable). SGD uses one sample per step (fast, noisy). Mini-batch GD (the standard) uses a batch of N samples — the best of both worlds.

---

*End of Batch 1 — AI Fundamentals*
