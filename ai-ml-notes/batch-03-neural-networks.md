# Batch 3 — Neural Networks & Deep Learning
> How machines learn through interconnected layers of math — and how to avoid the common pitfalls.

---

## 1. Neuron / Perceptron

**Definition**
The basic unit of a neural network. It takes multiple inputs, multiplies each by a weight, sums them up, adds a bias, and passes the result through an activation function to produce an output.

**Real-World Dev Example**
A spam filter neuron might take "contains 'free'", "has 3+ exclamation marks", and "unknown sender" as inputs, weight each by importance, and output a spam probability.

**ASCII Diagram**
```
x1 --w1--\
x2 --w2-- [Σ + bias] --> activation --> output
x3 --w3--/
```

**Gotchas & Dev Context**
- A single perceptron can only learn linearly separable data (XOR is impossible solo)
- Bias (`b`) shifts the activation threshold — never skip it
- "Neuron" and "perceptron" are often used interchangeably; technically the perceptron is the original 1950s model
- In PyTorch, a neuron is just `nn.Linear(in, out)` with one output node

**Production FAQ**

**Q: Why does my single-layer network fail on non-linear problems?**
A: A linear stack of neurons is still linear. You need non-linear activation functions *and* multiple layers to approximate complex functions.

**Q: How many neurons per layer should I start with?**
A: Common rule of thumb — start with 64–256, tune via validation loss. More neurons ≠ always better; you risk overfitting.

---

## 2. Activation Functions (ReLU, Sigmoid, Tanh, GELU, SiLU)

**Definition**
A non-linear function applied after a neuron's weighted sum to allow the network to learn complex patterns. Without it, stacking layers is mathematically equivalent to a single layer.

**Real-World Dev Example**
ReLU is used in most CV models (ResNet, VGG). GELU powers BERT and GPT. Sigmoid is used in binary classification output heads.

**ASCII Diagram**
```
ReLU:    f(x) = max(0, x)       /
                               /
         ___________________/
         0

Sigmoid: f(x) = 1/(1+e^-x)   S-shaped, output in (0,1)
Tanh:    f(x) = tanh(x)       S-shaped, output in (-1,1)
GELU:    smooth ReLU, used in Transformers
SiLU:    x * sigmoid(x), used in modern CNNs
```

**Gotchas & Dev Context**
- **Dead ReLU**: neurons outputting 0 forever when inputs stay negative → use Leaky ReLU or He init
- **Sigmoid saturates**: gradients near 0 or 1 vanish; avoid in hidden layers
- **Tanh** is preferred over sigmoid in hidden layers (zero-centered)
- **GELU/SiLU** are differentiable everywhere — smoother gradient flow
- Use `torch.nn.functional` for inline use vs. `nn.ReLU()` as a layer

**Production FAQ**

**Q: Which activation should I default to?**
A: ReLU for CNNs/MLPs. GELU for Transformers. Sigmoid/softmax only at output heads.

**Q: My loss is stuck and neurons aren't learning — why?**
A: Likely dead ReLU or vanishing gradients. Switch to LeakyReLU and check weight initialization.

---

## 3. Feedforward Neural Network

**Definition**
A neural network where data flows in one direction — input → hidden layers → output — with no cycles or feedback loops. Also called a Multi-Layer Perceptron (MLP).

**Real-World Dev Example**
Predicting house prices from tabular features (bedrooms, area, location) — you stack 2–3 dense layers and output a single value.

**ASCII Diagram**
```
Input Layer    Hidden Layer 1   Hidden Layer 2   Output
  [x1]  ---->   [h1][h2]  ---->   [h3][h4]  ---->  [y]
  [x2]  ---->   [h1][h2]  ---->   [h3][h4]  ---->  [y]
  [x3]  ---->
```

**Gotchas & Dev Context**
- "Feedforward" ≠ "simple" — GPT's per-token MLP block is a feedforward network
- Depth (more layers) helps generalization; width (more neurons) helps memorization
- Always normalize inputs before feeding; unnormalized inputs cause slow or failed training
- In PyTorch: chain `nn.Linear` → `nn.ReLU` blocks, use `nn.Sequential` for clarity

```python
model = nn.Sequential(
    nn.Linear(128, 256), nn.ReLU(),
    nn.Linear(256, 64),  nn.ReLU(),
    nn.Linear(64, 1)
)
```

**Production FAQ**

**Q: When should I use an MLP vs. a CNN or RNN?**
A: MLP for tabular/structured data. CNN for spatial data (images). RNN/Transformer for sequential data (text, time series).

**Q: How deep should I go?**
A: For tabular data, 2–4 layers is usually optimal. Deeper networks rarely help for non-image tasks and are harder to train.

---

## 4. Backpropagation

**Definition**
The algorithm that trains neural networks by calculating how much each weight contributed to the loss, then adjusting weights in the direction that reduces that loss — done via the chain rule of calculus.

**Real-World Dev Example**
After your image classifier predicts "cat" for a dog photo, backprop traces the error backwards through every layer, computing gradients so the optimizer can nudge each weight.

**ASCII Diagram**
```
Forward pass:  Input → Layer1 → Layer2 → Loss
Backward pass: Loss → ∂L/∂Layer2 → ∂L/∂Layer1 → update weights
```

**Gotchas & Dev Context**
- Backprop requires all operations to be **differentiable** — that's why most layers use smooth math
- PyTorch does this automatically via `.backward()` — you rarely implement it manually
- Gradients **accumulate** by default in PyTorch; call `optimizer.zero_grad()` before each batch
- Numerical precision matters — use `float32` minimum; `float16` can cause gradient underflow

```python
loss.backward()        # compute gradients
optimizer.step()       # update weights
optimizer.zero_grad()  # reset for next batch
```

**Production FAQ**

**Q: My gradients are None. Why?**
A: The tensor wasn't part of the computation graph. Ensure `requires_grad=True` and don't detach mid-forward-pass accidentally.

**Q: Is backprop the same as gradient descent?**
A: No. Backprop *computes* the gradients. Gradient descent (the optimizer) *uses* them to update weights.

---

## 5. Vanishing / Exploding Gradients

**Definition**
Vanishing gradients: gradients shrink toward zero as they flow back through layers, so early layers stop learning. Exploding gradients: the opposite — gradients grow exponentially, destabilizing training.

**Real-World Dev Example**
Training a deep RNN on long text sequences: the gradient for the first token becomes ~0 after 20 steps (vanishing), so the model can't learn long-range dependencies.

**ASCII Diagram**
```
Vanishing:  Loss → 0.001 → 0.0001 → 0.00001 → ≈0  (early layers freeze)
Exploding:  Loss → 100   → 10000  → NaN              (training crashes)
```

**Gotchas & Dev Context**
- Sigmoid/tanh activation are vanishing gradient prone → prefer ReLU+
- Deep networks (>10 layers) are especially vulnerable
- **Fixes for vanishing**: ResNet skip connections, LSTM/GRU gates, BatchNorm, better init
- **Fixes for exploding**: Gradient clipping (`torch.nn.utils.clip_grad_norm_`), careful LR
- Watch for `loss = NaN` — almost always exploding gradients

```python
# Gradient clipping in PyTorch
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

**Production FAQ**

**Q: How do I know if I have vanishing gradients?**
A: Log gradient norms per layer during training. If early-layer norms are near zero while later layers are large, you have vanishing gradients.

**Q: Does BatchNorm fully solve vanishing gradients?**
A: It helps significantly, but for very deep networks or RNNs, you still need architectural solutions (skip connections, LSTM gates).

---

## 6. Weight Initialization (Xavier, He, Kaiming)

**Definition**
The strategy used to set a neural network's weights before training begins. Poor initialization causes vanishing/exploding gradients from the very first forward pass.

**Real-World Dev Example**
Initializing all weights to zero causes every neuron to learn identically — the network never breaks symmetry. Xavier init prevents this for tanh networks; He init for ReLU networks.

**ASCII Diagram**
```
Xavier (Glorot):  W ~ Uniform(-√(6/(fan_in+fan_out)), +√(...))
He (Kaiming):     W ~ Normal(0, √(2/fan_in))   ← ReLU-aware
```

**Gotchas & Dev Context**
- **Never initialize all zeros** — breaks symmetry, all neurons learn the same thing
- **Xavier** assumes tanh/sigmoid activations (variance scales with fan_in + fan_out)
- **He/Kaiming** is Xavier adjusted for ReLU (accounts for half the neurons being zeroed)
- PyTorch defaults to Kaiming uniform for `nn.Linear` — usually fine out of the box
- For custom layers, explicitly init:

```python
nn.init.kaiming_normal_(layer.weight, nonlinearity='relu')
nn.init.xavier_uniform_(layer.weight)
```

**Production FAQ**

**Q: My transformer training diverges immediately — initialization issue?**
A: Likely. Transformers are sensitive; use scaled init (divide weights by √depth). GPT-2 uses `std = 0.02 / √(2 * num_layers)` for residual projections.

**Q: Does initialization matter less with BatchNorm?**
A: Less so, but still matters for training speed and early convergence. Don't skip it.

---

## 7. Batch Normalization

**Definition**
A technique that normalizes the activations of each layer across the current mini-batch, then applies learnable scale (γ) and shift (β) parameters. It stabilizes training and often allows higher learning rates.

**Real-World Dev Example**
ResNet uses BatchNorm after every convolutional layer. Without it, training a 50-layer network is nearly impossible due to internal covariate shift.

**ASCII Diagram**
```
Input batch x → μ,σ over batch → x̂ = (x-μ)/σ → γ·x̂ + β → next layer
```

**Gotchas & Dev Context**
- **Batch size matters**: BN breaks down with batch size < 8 — activations are too noisy
- At inference, BN uses **running mean/variance** collected during training, not live batch stats
- Always call `model.train()` / `model.eval()` — BN behavior differs between modes
- BN is placed **before** the activation function in most implementations
- BN doesn't work well with RNNs → use LayerNorm instead

```python
model.train()  # uses batch stats
model.eval()   # uses running stats (inference)
```

**Production FAQ**

**Q: Why does my model behave differently in train vs. eval mode?**
A: BatchNorm (and Dropout) are the culprits. Always call `model.eval()` before inference.

**Q: Should I use BN before or after activation?**
A: Convention varies. Original paper says before; many modern implementations place it before activation (pre-activation ResNet does the opposite intentionally).

---

## 8. Layer Normalization

**Definition**
Normalizes activations across the *feature* dimension for each individual sample, rather than across the batch. It's the standard for Transformers and sequence models.

**Real-World Dev Example**
GPT-2 and BERT use LayerNorm after every attention block and MLP block — it's what makes training stable at large scale.

**ASCII Diagram**
```
BatchNorm:  normalize across [batch] for each feature
LayerNorm:  normalize across [features] for each sample

Sample 1: [2.0, 4.0, 6.0] → normalized → [−1, 0, 1]
Sample 2: [1.0, 3.0, 5.0] → normalized independently
```

**Gotchas & Dev Context**
- LayerNorm is batch-size-independent — works with batch size 1
- Pre-LN (apply norm *before* attention) vs. Post-LN (after) — Pre-LN is more stable for deep transformers
- `nn.LayerNorm(normalized_shape)` where `normalized_shape` is the feature dim(s)
- Also has learnable γ (gain) and β (bias) — don't freeze them accidentally

```python
norm = nn.LayerNorm(d_model)  # for transformer hidden size
out = norm(x)                 # x shape: [batch, seq, d_model]
```

**Production FAQ**

**Q: When should I use LayerNorm over BatchNorm?**
A: Always use LayerNorm for NLP/Transformers. Use BatchNorm for CNNs with large batches.

**Q: Does LayerNorm slow down inference?**
A: Negligibly. The compute is O(d_model) per token, which is trivial vs. attention.

---

## 9. Dropout

**Definition**
A regularization technique that randomly sets a fraction of neurons to zero during training, forcing the network to learn redundant representations and preventing over-reliance on any single neuron.

**Real-World Dev Example**
A text classifier overfits the training set (99% train accuracy, 72% val). Adding `Dropout(p=0.3)` after each dense layer brings val accuracy up to 85%.

**ASCII Diagram**
```
Training:   [n1] [n2] [  ] [n4] [  ] [n6]  ← ~30% zeroed randomly
Inference:  [n1] [n2] [n3] [n4] [n5] [n6]  ← all active, scaled
```

**Gotchas & Dev Context**
- Dropout is **only active in `model.train()` mode** — automatically disabled in `model.eval()`
- PyTorch scales outputs by `1/(1-p)` during training (inverted dropout) so inference needs no adjustment
- Typical values: `p=0.1–0.3` for Transformers, `p=0.5` for dense layers in MLPs
- Don't use Dropout on BatchNorm layers — they interact poorly
- Too high dropout (`p > 0.6`) causes underfitting

```python
self.dropout = nn.Dropout(p=0.3)
x = self.dropout(x)  # only active during training
```

**Production FAQ**

**Q: I forgot `model.eval()` in production — what breaks?**
A: Dropout randomly zeros activations, making outputs non-deterministic and statistically wrong. Always call `model.eval()`.

**Q: Should I use dropout in Transformers?**
A: Yes, but lightly (p=0.1). It's applied to attention weights and MLP outputs in BERT/GPT.

---

## 10. Regularization (L1 / L2)

**Definition**
Techniques that add a penalty to the loss function based on the size of weights, discouraging the model from fitting noise and reducing overfitting.

**Real-World Dev Example**
A fraud detection MLP memorizes training data (AUC 0.99 train, 0.71 test). Adding L2 regularization (weight decay) brings test AUC to 0.88.

**ASCII Diagram**
```
L1: Loss_total = Loss + λ·Σ|w|     → drives weights to exactly 0 (sparse)
L2: Loss_total = Loss + λ·Σw²      → drives weights toward 0 (small)
```

**Gotchas & Dev Context**
- **L1** → sparsity (feature selection), useful when you want to auto-zero irrelevant features
- **L2** → smooth shrinkage; implemented as `weight_decay` in PyTorch optimizers
- L2 in PyTorch: just set `weight_decay=1e-4` in your optimizer — no loss modification needed
- L1 requires manual implementation (not built-in to optimizers)
- Elastic Net = L1 + L2 combined

```python
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
# weight_decay applies L2 automatically
```

**Production FAQ**

**Q: L2 vs. Dropout — which should I use?**
A: Both, together. L2 penalizes large weights globally; Dropout adds stochastic redundancy. They're complementary.

**Q: How do I pick λ (the regularization strength)?**
A: Tune on validation set. Start with `1e-4` for L2. Too high → underfitting; too low → no effect.

---

## 11. Convolutional Neural Network (CNN)

**Definition**
A neural network that uses convolution operations — sliding a small filter over input data — to detect local patterns like edges, textures, and shapes. Especially powerful for image and audio data.

**Real-World Dev Example**
A defect-detection system at a manufacturing plant uses a CNN to classify product photos as "pass" or "fail" by detecting surface cracks.

**ASCII Diagram**
```
Input image (5x5)   Filter (3x3)    Feature Map (3x3)
┌─────────────┐     ┌───────┐       ┌───────┐
│ 1 2 3 0 1  │  *  │ 1 0 1 │  =   │ dot   │
│ 0 1 2 3 0  │     │ 0 1 0 │       │product│
│ 1 0 1 2 3  │     │ 1 0 1 │       │ vals  │
└─────────────┘     └───────┘       └───────┘
      Slide filter across image, compute dot products
```

**Gotchas & Dev Context**
- Filters are learned, not handcrafted — the network finds what patterns matter
- `padding='same'` preserves spatial dimensions; without it, output shrinks
- More filters = more feature types detected per layer (e.g., 64 filters in conv1)
- Use `stride=2` instead of max pool where possible (modern practice)
- CNNs assume **spatial locality** — don't use them for tabular data

```python
nn.Conv2d(in_channels=3, out_channels=64, kernel_size=3, padding=1)
```

**Production FAQ**

**Q: How many conv layers do I need?**
A: For small images (32x32), 3–5 layers. For high-res, use a pretrained backbone (ResNet, EfficientNet) and fine-tune.

**Q: Why does my CNN run slow on CPU?**
A: Convolutions are highly parallelizable — always use GPU. For CPU deployment, use model quantization or ONNX.

---

## 12. Pooling (Max Pool, Average Pool)

**Definition**
A downsampling operation that reduces the spatial size of feature maps by summarizing a region with its max value or average, reducing computation and adding spatial invariance.

**Real-World Dev Example**
After detecting edge features with conv layers, max pooling keeps the "strongest" edge signal, making the model invariant to small shifts in the edge's exact position.

**ASCII Diagram**
```
Feature Map (4x4)     Max Pool 2x2     Pooled (2x2)
┌──────────────┐         │            ┌────────┐
│ 1  3  2  4  │   Max per 2x2 →      │ 3   4  │
│ 5  6  1  2  │   block              │ 6   9  │
│ 3  2  5  7  │                      └────────┘
│ 1  4  9  3  │
└──────────────┘
```

**Gotchas & Dev Context**
- **Max Pool**: retains strongest activation — preferred for classification
- **Avg Pool**: smooth representation — preferred for global context (Global Average Pooling at network end)
- Global Average Pooling (GAP) collapses entire spatial map to one value per channel — replaces flatten+dense in modern CNNs
- Pooling has **no learnable parameters** — just a fixed operation
- Stride-2 convolutions are increasingly replacing pooling for downsampling

```python
nn.MaxPool2d(kernel_size=2, stride=2)
nn.AdaptiveAvgPool2d((1, 1))  # Global Average Pooling
```

**Production FAQ**

**Q: Max pool vs. stride-2 conv — which is better?**
A: Stride-2 conv is generally preferred in modern architectures (EfficientNet, ConvNeXt) since it's learnable. Max pool is simpler and still fine for most tasks.

**Q: Why use Global Average Pooling instead of Flatten?**
A: GAP produces a fixed-size output regardless of input resolution and has far fewer parameters, reducing overfitting.

---

## 13. Recurrent Neural Network (RNN)

**Definition**
A neural network with a feedback loop — the output (hidden state) from the previous time step is fed back as input to the current step. Designed for sequential data.

**Real-World Dev Example**
A stock price forecaster feeds yesterday's prediction back into today's computation, letting the model maintain a "memory" of recent price trends.

**ASCII Diagram**
```
        h0       h1       h2       h3
        ↑        ↑        ↑        ↑
x1 → [RNN] → [RNN] → [RNN] → [RNN] → output
        ↗        ↗        ↗
    (hidden state passed forward)
```

**Gotchas & Dev Context**
- Vanilla RNNs suffer severely from vanishing gradients — practically useless for sequences > 20 steps
- Use **LSTM or GRU** instead for real tasks — vanilla RNN is mostly educational
- `batch_first=True` in PyTorch's `nn.RNN` changes input shape to `[batch, seq, features]` — always set this explicitly
- RNNs are sequential by nature — can't be parallelized across time steps (unlike Transformers)
- Still useful for short sequences with tight latency constraints

```python
rnn = nn.RNN(input_size=10, hidden_size=64, batch_first=True)
output, h_n = rnn(x)
```

**Production FAQ**

**Q: Should I use RNN or Transformer for NLP in 2024?**
A: Transformer for most NLP tasks. RNN only if you have very tight memory/latency constraints or streaming inference requirements.

**Q: My RNN isn't learning long-range dependencies. Why?**
A: Vanishing gradients. Switch to LSTM or GRU, which have gating mechanisms to preserve long-range information.

---

## 14. LSTM (Long Short-Term Memory)

**Definition**
An advanced RNN variant with a **cell state** (long-term memory) and three gates (input, forget, output) that control what information to keep, discard, or expose at each time step.

**Real-World Dev Example**
A sentiment analysis model reading "The food was terrible, BUT the service was excellent" needs to remember the contrast — LSTM's cell state holds that context across many tokens.

**ASCII Diagram**
```
        ┌──────────────────────────────────┐
        │  Cell State (long-term memory)   │ ──────────────→
        │  ────────────────────────────    │
        │  Forget  Input   Output          │
        │  Gate    Gate    Gate            │
        └──────────────────────────────────┘
         ↑ ht-1 (short-term)       → ht (output)
```

**Gotchas & Dev Context**
- 4× more parameters than a vanilla RNN — slower to train
- `nn.LSTM` returns `(output, (h_n, c_n))` — both hidden state AND cell state
- Use `bidirectional=True` for tasks where future context helps (e.g., NER, not language generation)
- Always initialize hidden states to zeros for new sequences
- Don't use LSTM for very long documents — Transformer handles that better

```python
lstm = nn.LSTM(input_size=10, hidden_size=64, batch_first=True)
output, (h_n, c_n) = lstm(x)
```

**Production FAQ**

**Q: LSTM vs. GRU — which should I default to?**
A: GRU for simpler problems and faster training. LSTM for complex tasks needing finer memory control. Benchmark both.

**Q: My LSTM outputs are all the same. What's wrong?**
A: Hidden state not reset between unrelated sequences. Call `h0 = torch.zeros(...)` at the start of each new batch.

---

## 15. GRU (Gated Recurrent Unit)

**Definition**
A streamlined RNN variant with two gates (reset, update) instead of LSTM's three, merging cell and hidden state. Fewer parameters, comparable performance, faster training.

**Real-World Dev Example**
A real-time autocomplete system uses GRU instead of LSTM to hit lower latency targets while still handling 30-word context windows effectively.

**ASCII Diagram**
```
LSTM: [Forget Gate] [Input Gate] [Output Gate] + Cell State
GRU:  [Reset Gate]  [Update Gate]              (no separate cell state)
```

**Gotchas & Dev Context**
- GRU has ~2/3 the parameters of an LSTM of the same hidden size → faster inference
- `nn.GRU` returns `(output, h_n)` — only one hidden state, no cell state
- GRU tends to match LSTM on most tasks but can underperform on very long, complex sequences
- Same `batch_first=True` caveat as RNN/LSTM
- On small datasets, GRU often generalizes *better* than LSTM due to fewer parameters to overfit

```python
gru = nn.GRU(input_size=10, hidden_size=64, batch_first=True)
output, h_n = gru(x)  # no c_n unlike LSTM
```

**Production FAQ**

**Q: Can I mix LSTM and GRU layers in one model?**
A: Technically yes, but rarely beneficial. Stick to one type; mixing complicates state management.

**Q: GRU trains faster — does it also infer faster?**
A: Yes — fewer matrix multiplications per step. For latency-sensitive serving (e.g., < 10ms), GRU is the better default over LSTM.

---

## 16. Sequence-to-Sequence (Seq2Seq)

**Definition**
An architecture that maps an input sequence to an output sequence of (potentially) different length, using an **encoder** to compress the input into a context vector and a **decoder** to generate the output.

**Real-World Dev Example**
Machine translation: encoder reads "How are you?" in English, produces a context vector; decoder generates "¿Cómo estás?" in Spanish token by token.

**ASCII Diagram**
```
Input:   "How are you?"
          ↓
   [Encoder RNN/LSTM]
          ↓
    [Context Vector]
          ↓
   [Decoder RNN/LSTM] → "¿Cómo" → "estás?" → <EOS>
```

**Gotchas & Dev Context**
- The fixed-size context vector is a bottleneck — **Attention mechanism** was invented to fix this
- Teacher forcing during training: feed the *correct* previous token to the decoder instead of its own prediction
- **Exposure bias**: at inference the decoder sees its own (possibly wrong) outputs — can accumulate errors
- Modern NLP replaced RNN-based Seq2Seq with Transformer encoder-decoder (e.g., T5, BART, mT5)
- Still relevant for structured outputs like code generation and SQL query generation

**Production FAQ**

**Q: My Seq2Seq model generates repetitive output. Why?**
A: Beam search with no length penalty causes repetition. Use diverse beam search or sampling with temperature.

**Q: Should I build Seq2Seq from scratch or use a pretrained model?**
A: Use pretrained (T5, BART) and fine-tune. Building from scratch is only justified for research or highly domain-specific sequences.

---

## 17. Autoencoder

**Definition**
A neural network trained to compress input data into a smaller latent representation (encode) and then reconstruct the original input from that representation (decode). The goal is to learn efficient data representations.

**Real-World Dev Example**
An anomaly detection system trains an autoencoder on normal network traffic. At inference, unusually high reconstruction error signals a potential intrusion.

**ASCII Diagram**
```
Input (784)  → Encoder → Latent (32) → Decoder → Output (784)
[image]       compress    bottleneck    expand    [reconstruction]

Reconstruction loss = MSE(input, output)
```

**Gotchas & Dev Context**
- The bottleneck forces the model to learn only the most important features
- Reconstruction loss (MSE or BCE) is the training signal — no labels needed (unsupervised)
- Autoencoders don't generate *new* data well — that's VAE's job
- Use cases: anomaly detection, denoising (denoising autoencoders), dimensionality reduction
- **Denoising autoencoder**: inject noise into input, train to reconstruct clean version — forces robust features

```python
# Encoder-decoder symmetry
encoder = nn.Sequential(nn.Linear(784, 256), nn.ReLU(), nn.Linear(256, 32))
decoder = nn.Sequential(nn.Linear(32, 256), nn.ReLU(), nn.Linear(256, 784))
```

**Production FAQ**

**Q: Autoencoder vs. PCA for dimensionality reduction?**
A: Autoencoder captures non-linear structure; PCA is linear only. Use AE for complex data (images), PCA for quick tabular analysis.

**Q: My autoencoder memorizes the training data. How do I fix it?**
A: Reduce latent size, add Dropout, or use a denoising setup. A too-large latent just copies inputs.

---

## 18. Variational Autoencoder (VAE)

**Definition**
An autoencoder that encodes inputs as **probability distributions** (mean + variance) rather than fixed vectors, enabling it to generate new, realistic samples by sampling from the learned latent space.

**Real-World Dev Example**
A VAE trained on face images can generate novel photorealistic faces by sampling from its latent space — interpolating between "young" and "old" in latent space produces smooth face aging.

**ASCII Diagram**
```
Input → Encoder → μ, σ (mean, std)
                     ↓
              z = μ + σ·ε   (ε ~ N(0,1))  ← reparameterization trick
                     ↓
             Decoder → Reconstruction
```

**Gotchas & Dev Context**
- Loss = **Reconstruction loss** + **KL Divergence** (keeps latent space regular)
- **KL Divergence** forces the latent distribution toward a standard normal — enables random sampling
- **Reparameterization trick**: `z = μ + σ * ε` where ε is random noise — makes backprop work through sampling
- VAE outputs are often blurry vs. GAN outputs — VAE optimizes MSE/BCE which averages pixels
- KL weight (β) is a key hyperparameter: too high → blurry reconstructions; too low → no structure in latent space

**Production FAQ**

**Q: VAE vs. GAN for image generation?**
A: GAN produces sharper images; VAE has a structured latent space enabling interpolation and attribute editing. Use GANs for quality, VAEs for control.

**Q: My VAE collapsed — all outputs look the same. Why?**
A: KL divergence is dominating, collapsing the posterior to the prior. Reduce β or use KL annealing (warm up β from 0).

---

## 19. Generative Adversarial Network (GAN)

**Definition**
A framework of two competing networks: a **Generator** that creates fake data, and a **Discriminator** that tries to distinguish real from fake. They train adversarially until the generator fools the discriminator.

**Real-World Dev Example**
StyleGAN generates photorealistic human faces that don't exist. Fashion brands use GANs to generate product image variations without photo shoots.

**ASCII Diagram**
```
Random Noise → [Generator] → Fake Image ──┐
                                           ↓
Real Images ──────────────────────────> [Discriminator] → Real/Fake?
                                           ↑
         Generator tries to fool it ───────┘
```

**Gotchas & Dev Context**
- **Mode collapse**: Generator finds one output that always fools the discriminator — diversity dies; use Wasserstein GAN (WGAN) or minibatch discrimination to fix
- Training is notoriously **unstable** — balance between G and D is delicate
- If Discriminator is too strong → Generator can't learn (gradients vanish); too weak → Generator exploits trivial patterns
- Monitor both G loss and D loss — they should oscillate, not diverge
- Use `torch.no_grad()` when updating Generator to avoid backpropping through Discriminator

**Production FAQ**

**Q: How do I evaluate GAN quality objectively?**
A: Use **FID (Fréchet Inception Distance)** — lower is better. Also check **IS (Inception Score)** for diversity.

**Q: GAN training crashed after 500 steps. What happened?**
A: Likely mode collapse or Discriminator dominating. Reduce D learning rate, add gradient penalty (WGAN-GP), or use spectral normalization.

---

## 20. Skip Connections / Residual Networks (ResNet)

**Definition**
Skip connections (a.k.a. residual connections) add the input of a layer block directly to its output, allowing gradients to flow directly through the network without passing through every transformation. The foundation of ResNet.

**Real-World Dev Example**
ResNet-50, trained on ImageNet, uses skip connections to successfully train 50 layers — something impossible with plain networks due to vanishing gradients. It remains a backbone for transfer learning across CV tasks.

**ASCII Diagram**
```
Without skip:  x → [Conv→BN→ReLU→Conv→BN] → out

With skip:     x → [Conv→BN→ReLU→Conv→BN] → (+x) → ReLU → out
               └────────────────────────────↗
                        (identity shortcut)
```

**Gotchas & Dev Context**
- The residual block learns `F(x) = output - x` (the *residual*), not the full mapping — easier to optimize
- If input and output dimensions differ, use a 1×1 projection conv on the skip path to match shapes
- Skip connections are also used in Transformers (attention output + residual) and U-Net (encoder to decoder)
- They help with vanishing gradients by providing a gradient "highway"
- Pre-activation ResNet (BN → ReLU → Conv) often outperforms original

```python
class ResidualBlock(nn.Module):
    def forward(self, x):
        return F.relu(self.conv_block(x) + x)  # skip connection
```

**Production FAQ**

**Q: Why does adding more layers hurt accuracy without skip connections?**
A: Deep networks without skip connections suffer degradation — not just overfitting but actually *lower training accuracy*. The identity shortcut lets the network at minimum "do nothing" and not degrade.

**Q: Are skip connections only for ResNet?**
A: No — they're in DenseNet, U-Net (encoder→decoder bridges), every Transformer block, and EfficientNet. They're a universal deep learning tool.

---

*End of Batch 3 — Neural Networks & Deep Learning*
