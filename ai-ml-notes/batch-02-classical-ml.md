# Batch 2 — Classical ML Algorithms
> The battle-tested algorithms that still power most production ML systems today.

---

## 1. Linear Regression

### Definition
Fits a straight line through data to predict a **continuous numeric output** (e.g., price, temperature) by minimizing the difference between predicted and actual values.

### Real-World Dev Example
Predicting a house's sale price based on square footage, number of rooms, and age of the building.

```python
from sklearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(X_train, y_train)
print(model.coef_)  # weight for each feature
```

### ASCII Diagram
```
Price
  |          *  (predicted line)
  |       /
  |    /  *
  | / *
  |/ *
  +-------------> Square Footage
```

### Gotchas & Dev Context
- Assumes a **linear relationship** — if the true pattern is curved, the model fails silently (low R²).
- **Sensitive to outliers**: one extreme data point can drag the line significantly.
- Always check **residual plots** — random scatter = good fit; patterns = use a different model.
- Regularized variants: **Ridge** (L2) and **Lasso** (L1) prevent overfitting on high-dimensional data.

### Production FAQ
**Q: My predictions are off even though training R² is high — why?**
A: You're likely overfitting. Use Ridge/Lasso or check for multicollinearity between features.

**Q: When should I use Linear Regression vs. a neural network?**
A: Prefer Linear Regression when data is small, relationships are linear, and interpretability matters. Neural networks are overkill for simple tabular regression.

---

## 2. Logistic Regression

### Definition
Predicts a **probability between 0 and 1** for a class label (e.g., spam/not spam) by running a linear equation through a sigmoid function. Despite the name, it's a **classification** algorithm.

### Real-World Dev Example
Email spam detection: input is word frequencies, output is P(spam) — threshold at 0.5 to classify.

```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression()
model.fit(X_train, y_train)
proba = model.predict_proba(X_test)[:, 1]  # P(positive class)
```

### ASCII Diagram
```
Output (probability)
  1 |          ____-----
    |       --/
  0.5|      /
    |   --/
  0 |--/
    +-----------------------> Linear Score (z)
         sigmoid(z) = 1 / (1 + e^-z)
```

### Gotchas & Dev Context
- Default threshold is **0.5** — adjust it based on business cost (false negatives in fraud = expensive).
- Works well for **linearly separable** classes; use kernel SVM or tree models for complex boundaries.
- Regularization (`C` parameter in sklearn) is on by default — tune it!
- For multi-class problems, use `multi_class='multinomial'` or One-vs-Rest.

### Production FAQ
**Q: Logistic Regression gives 92% accuracy on fraud detection — is that good?**
A: Probably not. If 92% of transactions are legitimate, a model that predicts "not fraud" every time achieves 92%. Check precision, recall, and F1.

**Q: Can Logistic Regression output probabilities directly?**
A: Yes — use `predict_proba()`. These are calibrated probabilities, making them useful for ranking and threshold tuning.

---

## 3. Decision Tree

### Definition
A flowchart-like model that splits data based on feature thresholds to make predictions. Each internal node is a question; each leaf is a prediction.

### Real-World Dev Example
A bank's loan approval system: "Is income > $50k? → Yes: Is credit score > 700? → Yes: Approve."

### ASCII Diagram
```
        [Income > $50k?]
         /            \
       Yes             No
  [Credit > 700?]   [DENY]
    /       \
  Yes        No
[APPROVE]  [DENY]
```

### Gotchas & Dev Context
- **Prone to overfitting** — a deep tree memorizes training data. Always set `max_depth` or `min_samples_leaf`.
- Decision boundaries are always **axis-aligned** (horizontal/vertical splits) — can't capture diagonal patterns naturally.
- **Interpretable**: you can export and read the actual rules (great for compliance/audit).
- Feature importance scores come for free — useful for feature selection.

### Production FAQ
**Q: My Decision Tree gets 99% train accuracy but 65% test accuracy — what do I do?**
A: It's overfit. Prune it: reduce `max_depth`, increase `min_samples_split`, or switch to Random Forest.

**Q: How does a Decision Tree handle categorical features?**
A: sklearn requires numerical input — you must encode categoricals first. Libraries like LightGBM handle raw categoricals natively.

---

## 4. Random Forest

### Definition
An **ensemble of Decision Trees**, each trained on a random subset of data and features, with the final prediction made by majority vote (classification) or averaging (regression). More robust than a single tree.

### Real-World Dev Example
Predicting customer churn: trains 100 trees on different data samples; each votes, and the majority wins.

```python
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
model.fit(X_train, y_train)
print(model.feature_importances_)
```

### Gotchas & Dev Context
- **Reduces variance** (overfitting) compared to a single tree via bagging + feature randomness.
- More trees = more stable, but **diminishing returns** past ~200 trees. Monitor OOB error.
- Slower to predict than a single tree — matters at high-throughput inference.
- **Does not extrapolate**: predictions are bounded by training data range (unlike linear models).
- Great baseline — beat it before reaching for XGBoost or neural nets.

### Production FAQ
**Q: Random Forest vs. Gradient Boosting — which should I try first?**
A: Start with Random Forest (faster to tune, parallelizable, less overfit risk). Move to gradient boosting if you need that extra 1–3% performance.

**Q: How do I get feature importance from a Random Forest?**
A: Use `model.feature_importances_` (sklearn). For a more reliable estimate, use permutation importance — it's less biased toward high-cardinality features.

---

## 5. Gradient Boosting (XGBoost, LightGBM, CatBoost)

### Definition
Builds trees **sequentially**, where each new tree corrects the errors of the previous one. The result is a powerful ensemble that gradually "boosts" accuracy. XGBoost, LightGBM, and CatBoost are optimized implementations.

### Real-World Dev Example
Kaggle competition tabular tasks, credit scoring, click-through rate prediction — gradient boosting consistently tops leaderboards.

```python
import xgboost as xgb
model = xgb.XGBClassifier(n_estimators=500, learning_rate=0.05, max_depth=6)
model.fit(X_train, y_train, eval_set=[(X_val, y_val)], early_stopping_rounds=20)
```

### Gotchas & Dev Context
- **More hyperparameters** to tune than Random Forest: `learning_rate`, `max_depth`, `subsample`, `colsample_bytree`.
- Use **early stopping** — without it, the model will overfit given enough trees.
- **LightGBM** is fastest for large datasets (histogram-based). **CatBoost** handles categoricals natively. **XGBoost** is most widely supported.
- Lower `learning_rate` + more trees = usually better, but slower training.

### Production FAQ
**Q: XGBoost vs. LightGBM — when does it matter?**
A: On datasets > 100k rows, LightGBM is typically 5–10× faster to train. For smaller data, the difference is negligible.

**Q: My gradient boosting model is overfitting — what do I tune first?**
A: Reduce `max_depth` (try 3–6), lower `learning_rate`, and increase `min_child_weight`. Always use early stopping on a validation set.

---

## 6. Support Vector Machine (SVM)

### Definition
Finds the **optimal hyperplane** that separates classes with the **maximum margin** between them. Data points closest to the boundary are called support vectors.

### Real-World Dev Example
Text classification (e.g., sentiment analysis) on small datasets — SVMs with TF-IDF features were the go-to before deep learning.

### ASCII Diagram
```
Class A: *   Class B: o

  *  *  |  o  o
  *     |     o
  * *   |   o o
      Margin
  <-----|----->
    Hyperplane (decision boundary)
```

### Gotchas & Dev Context
- The **kernel trick** (RBF, polynomial) lets SVM classify non-linearly separable data — but picking the right kernel matters.
- **Doesn't scale well**: O(n²–n³) training time. Avoid on datasets > 100k rows.
- **Sensitive to feature scaling** — always normalize/standardize before training.
- The `C` parameter controls the margin: high C = strict (low bias, high variance); low C = soft margin (more tolerant of misclassification).

### Production FAQ
**Q: SVM or Logistic Regression for text classification?**
A: Both work well on sparse TF-IDF features. SVM (LinearSVC) often edges out LR on small datasets. On large data, use LR with SGD or fine-tuned transformers.

**Q: Why is my SVM training taking forever?**
A: SVMs are O(n²–n³). Use `LinearSVC` for large datasets (linear kernel only, much faster) or switch to gradient boosting.

---

## 7. K-Nearest Neighbors (KNN)

### Definition
Classifies a new data point by looking at the **K closest points** in the training set and taking a majority vote. No training phase — it memorizes the data.

### Real-World Dev Example
Product recommendation: "Users similar to you (KNN in user-feature space) also bought these items."

### ASCII Diagram
```
  K=3: Find 3 nearest neighbors
       *  (Class A)
   ? ←  ← o  (Class B)
       *  (Class A)
   → Majority vote: Class A wins
```

### Gotchas & Dev Context
- **Lazy learner**: no training, but prediction is O(n × d) — slow at inference for large datasets.
- **Curse of dimensionality**: distances become meaningless in high dimensions. Apply PCA first.
- Always **scale features** — KNN uses distance, so a feature in thousands dominates one in single digits.
- Use `KD-Tree` or `Ball-Tree` indices (`algorithm='kd_tree'` in sklearn) to speed up neighbor search.

### Production FAQ
**Q: How do I pick K?**
A: Cross-validate over a range (e.g., K = 1 to 30). Odd K avoids ties in binary classification. Larger K = smoother boundary but may underfit.

**Q: KNN is too slow for production — what are the alternatives?**
A: Use Approximate Nearest Neighbor libraries: **FAISS** (Meta), **Annoy** (Spotify), or **ScaNN** (Google). These trade tiny accuracy for massive speed gains.

---

## 8. K-Means Clustering

### Definition
Partitions data into **K clusters** by iteratively assigning points to the nearest centroid and updating centroids until convergence. An **unsupervised** algorithm — no labels needed.

### Real-World Dev Example
Customer segmentation: group 1M users into 5 behavioral segments to target with different marketing campaigns.

```python
from sklearn.cluster import KMeans
model = KMeans(n_clusters=5, random_state=42, n_init='auto')
model.fit(X)
labels = model.labels_
```

### ASCII Diagram
```
Before:  . . . . . . . .   (raw data)
After:   [A A] [B B B] [C C]  (3 clusters)
          ↑       ↑       ↑
       centroid centroid centroid
```

### Gotchas & Dev Context
- **You must choose K** — use the **Elbow method** (plot inertia vs. K) or **Silhouette score**.
- Results depend on **random initialization** — use `n_init=10` to run multiple times and take the best.
- Assumes **spherical, equally sized clusters** — fails on elongated or density-varying shapes (use DBSCAN instead).
- Sensitive to outliers and feature scale — always normalize first.

### Production FAQ
**Q: How do I know if my clusters are actually meaningful?**
A: Compute Silhouette Score (>0.5 is decent) and inspect cluster statistics manually. Business validation matters more than metrics.

**Q: K-Means won't converge on my data — why?**
A: Likely outliers or wrong K. Try `init='k-means++'` (default in sklearn), remove outliers, and validate K with Elbow/Silhouette.

---

## 9. DBSCAN

### Definition
**Density-Based Spatial Clustering of Applications with Noise** — groups points that are closely packed together and labels sparse points as **outliers/noise**. Doesn't need K specified upfront.

### Real-World Dev Example
Fraud detection: cluster normal transactions by density; sparse outlier points flagged as anomalies.

### ASCII Diagram
```
  . . . .      * * *
  . . . .  (noise)  * * *   ← 2 clusters found
  . . . .      * * *
     (Cluster 1)   (Cluster 2)
```

### Gotchas & Dev Context
- Two key parameters: **`eps`** (neighborhood radius) and **`min_samples`** (minimum points to form a cluster). Both require tuning.
- Use a **k-distance plot** to choose `eps`: find the "elbow" in the sorted distance graph.
- Struggles with **varying density clusters** — HDBSCAN is the modern, more robust alternative.
- Does **not** produce centroids — can't directly assign new points to clusters at inference.

### Production FAQ
**Q: DBSCAN says most of my data is noise — what went wrong?**
A: `eps` is too small. Increase it. Plot the k-distance graph (k = `min_samples`) and find the elbow point.

**Q: DBSCAN vs. K-Means — when do I prefer DBSCAN?**
A: Use DBSCAN when you don't know K, expect irregular cluster shapes, or need outlier detection built in. Use K-Means when you want fast, scalable, convex clusters.

---

## 10. Principal Component Analysis (PCA)

### Definition
A **dimensionality reduction** technique that transforms features into a new set of uncorrelated axes (principal components) ordered by the variance they explain — letting you discard low-information dimensions.

### Real-World Dev Example
Reducing 500 pixel-based image features to 50 principal components before feeding them into a classifier — same accuracy, 10× faster training.

```python
from sklearn.decomposition import PCA
pca = PCA(n_components=50)
X_reduced = pca.fit_transform(X)
print(pca.explained_variance_ratio_.cumsum())  # how much variance retained
```

### ASCII Diagram
```
Original 2D:         After PCA (1D):
   *  *                → PC1 axis
  *  *  *         * * * * * * *  (projected)
   *  *
  (2 features)        (1 feature)
```

### Gotchas & Dev Context
- PCA is **linear** — it won't capture non-linear structure. Use **t-SNE** or **UMAP** for visualization.
- **Always scale features first** — PCA is variance-sensitive; large-scale features dominate.
- Choose components by targeting **95% explained variance** as a starting heuristic.
- PCA components are **not interpretable** — you lose the original feature names.

### Production FAQ
**Q: How many components should I keep?**
A: Plot the cumulative `explained_variance_ratio_` and cut off at 95%. Or tune `n_components` via cross-validation on downstream task performance.

**Q: Can I use PCA to remove multicollinearity before Linear Regression?**
A: Yes — this is called **Principal Component Regression (PCR)**. But consider Ridge Regression first; it's simpler and often equally effective.

---

## 11. Dimensionality Reduction

### Definition
The process of **reducing the number of features** in a dataset while preserving as much useful information as possible — combating the curse of dimensionality and speeding up training.

### Real-World Dev Example
A genomics dataset has 20,000 gene expression features. Reducing to 100 via PCA + UMAP makes visualization and ML feasible.

### Gotchas & Dev Context
- **Two types**: Feature Selection (keep original features) vs. Feature Extraction (create new ones like PCA).
- Common techniques:

| Technique | Type | Best For |
|-----------|------|----------|
| PCA | Extraction | Linear data, preprocessing |
| t-SNE | Extraction | 2D/3D visualization only |
| UMAP | Extraction | Visualization + general reduction |
| LDA | Extraction | Supervised (class-aware) |
| SelectKBest | Selection | Fast feature pruning |

- **t-SNE is not for training** — it's a visualization tool; don't feed t-SNE output to a model.
- Dimensionality reduction can **hurt performance** if important features get compressed out — always validate on downstream task.

### Production FAQ
**Q: Should I reduce dimensions before or after train/test split?**
A: **Always fit the reducer on training data only**, then transform both train and test. Fitting on all data leaks test info.

**Q: UMAP vs. t-SNE — which should I use?**
A: UMAP is faster, scales better, and preserves global structure better. Prefer UMAP for modern workflows.

---

## 12. Feature Engineering

### Definition
The process of **creating, transforming, or selecting input features** to make patterns more accessible to ML models — often the highest-leverage activity in an ML project.

### Real-World Dev Example
From a raw `timestamp` column, engineer: `hour_of_day`, `is_weekend`, `days_since_last_purchase` — features a model can actually learn from.

```python
df['hour'] = df['timestamp'].dt.hour
df['is_weekend'] = df['timestamp'].dt.dayofweek >= 5
df['days_since'] = (pd.Timestamp.now() - df['last_purchase']).dt.days
```

### Gotchas & Dev Context
- **Domain knowledge wins**: the best features come from understanding the problem, not automated tools.
- Common transformations: log-transform skewed variables, bin continuous variables, create interaction terms (`A × B`).
- **Target encoding** (mean of target per category) is powerful but must be done with cross-validation to avoid leakage.
- Automated Feature Engineering tools: **Featuretools**, **AutoFeat** — useful but not a substitute for domain insight.
- Always engineer features **after** the train/test split to prevent leakage.

### Production FAQ
**Q: How do I know which engineered features are actually helping?**
A: Use feature importance (tree models), permutation importance, or SHAP values. Remove features that don't improve cross-validation score.

**Q: Is feature engineering still relevant with deep learning?**
A: Less so for unstructured data (images, text). For tabular data, it still often gives better results than raw features fed into neural networks.

---

## 13. Feature Scaling (Normalization, Standardization)

### Definition
Rescaling feature values so they fall on a **comparable range**, preventing features with large values from dominating distance- or gradient-based models.

### Real-World Dev Example
A dataset has `age` (18–90) and `income` (20,000–200,000). Without scaling, income dominates KNN distances and gradient descent.

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# Standardization: mean=0, std=1
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)

# Normalization: range [0, 1]
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X_train)
```

### Gotchas & Dev Context
- **When to use which:**
  - `StandardScaler` — when data is roughly Gaussian or for PCA, SVM, Logistic Regression.
  - `MinMaxScaler` — when you need bounded output (e.g., neural network input layers).
  - `RobustScaler` — when data has outliers (scales using IQR instead of mean/std).
- **Tree-based models (RF, XGBoost) don't need scaling** — they split on thresholds, not distances.
- **Fit on train only**: `fit_transform(X_train)`, then `transform(X_test)`. Never fit on test data.

### Production FAQ
**Q: I forgot to scale — model trained. Can I scale after?**
A: No — retrain with scaling applied at the start of the pipeline. Use `sklearn.pipeline.Pipeline` to enforce correct order automatically.

**Q: Does scaling affect model accuracy for tree models?**
A: No effect on split-based models (Decision Tree, Random Forest, XGBoost). It matters for SVM, KNN, Logistic Regression, and Neural Networks.

---

## 14. One-Hot Encoding / Label Encoding

### Definition
Techniques to convert **categorical text values into numbers** so ML models can process them. Label Encoding assigns integers; One-Hot Encoding creates binary columns per category.

### Real-World Dev Example
Color feature: `["red", "blue", "green"]`
- **Label Encoding**: red=0, blue=1, green=2 *(implies ordering — bad for non-ordinal data)*
- **One-Hot Encoding**: `[1,0,0]`, `[0,1,0]`, `[0,0,1]`

```python
import pandas as pd
# One-Hot
df = pd.get_dummies(df, columns=['color'], drop_first=True)

# Label Encoding (ordinal only)
from sklearn.preprocessing import LabelEncoder
df['size'] = LabelEncoder().fit_transform(df['size'])
```

### Gotchas & Dev Context
- **Never use Label Encoding for nominal categories** (e.g., city names) — the model will falsely interpret order/distance.
- **High cardinality** (e.g., 10,000 zip codes) → One-Hot creates 10,000 columns. Use **Target Encoding** or **Embedding layers** instead.
- Drop one column with `drop_first=True` to avoid the **dummy variable trap** (multicollinearity).
- In production, handle **unseen categories** explicitly — sklearn's `OrdinalEncoder` has an `handle_unknown` parameter.

### Production FAQ
**Q: My model never saw category "X" during training — it crashes in prod. How to fix?**
A: Use `handle_unknown='ignore'` in `OneHotEncoder`. Or use a catch-all "unknown" bucket at preprocessing time.

**Q: When should I use Target Encoding over One-Hot?**
A: When cardinality is high (>20 categories). Always use cross-validation-based target encoding (e.g., `category_encoders.TargetEncoder`) to prevent leakage.

---

## 15. Handling Missing Data

### Definition
Strategies to deal with **null/NaN values** in a dataset — because most real-world data is incomplete and models can't process NaNs natively.

### Real-World Dev Example
A medical dataset has 15% missing values in `cholesterol_level`. Dropping those rows loses too much data — better to impute with median.

```python
from sklearn.impute import SimpleImputer, KNNImputer

# Median imputation (robust to outliers)
imp = SimpleImputer(strategy='median')
X_imputed = imp.fit_transform(X)

# KNN imputation (uses similar rows)
imp = KNNImputer(n_neighbors=5)
X_imputed = imp.fit_transform(X)
```

### Gotchas & Dev Context
- **Types of missingness** matter:
  - MCAR (random) → safe to impute.
  - MAR (depends on other features) → conditional imputation.
  - MNAR (missing because of the value itself) → dangerous; imputation can introduce bias.
- **Add a "was_missing" flag column** alongside imputed values — it can be a predictive signal.
- Tree models (XGBoost, LightGBM) handle NaNs **natively** — no imputation needed.
- Never impute test data based on test statistics — **fit imputer on training data only**.

### Production FAQ
**Q: Should I drop rows or impute when data is missing?**
A: Impute unless >40–50% of a column is missing and it has no predictive value. Dropping rows wastes data and can bias the distribution.

**Q: Is mean or median imputation better?**
A: Median is safer — mean is heavily affected by outliers. For categorical features, use mode imputation.

---

## 16. Imbalanced Datasets (SMOTE, Class Weights)

### Definition
When one class has **far more examples** than another (e.g., 99% non-fraud, 1% fraud), models bias toward the majority class. Techniques like SMOTE and class weighting counteract this.

### Real-World Dev Example
Credit card fraud: 99,000 normal vs. 1,000 fraud transactions. A model predicting "no fraud" every time is 99% accurate but useless.

```python
# Class weights (built-in, preferred)
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(class_weight='balanced')

# SMOTE (oversampling minority class)
from imblearn.over_sampling import SMOTE
X_res, y_res = SMOTE().fit_resample(X_train, y_train)
```

### Gotchas & Dev Context
- **Use class weights first** — it's free, simple, and often just as effective as SMOTE.
- **SMOTE** generates synthetic minority samples by interpolating between existing ones — can introduce noise.
- **Never SMOTE the test set** — only resample training data.
- Evaluate with **F1, precision-recall, ROC-AUC** — not accuracy. Accuracy is meaningless on imbalanced data.
- For extreme imbalance (1:1000+), consider **anomaly detection** approaches instead.

### Production FAQ
**Q: SMOTE improved my training F1 but not test F1 — why?**
A: SMOTE can cause overfitting to synthetic points. Try `class_weight='balanced'` instead, or use SMOTE + Tomek Links (combined cleaning).

**Q: What's the right sampling ratio for SMOTE?**
A: You don't need 50/50. Experiment with ratios like 1:5 or 1:10 — full balance often hurts generalization.

---

## 17. Confusion Matrix / Precision / Recall / F1

### Definition
Tools to evaluate **classification model performance** beyond raw accuracy — especially important when classes are imbalanced.

### Real-World Dev Example
Medical test for a disease: a false negative (missed disease) is worse than a false positive → optimize for **Recall**.

### ASCII Diagram
```
                  Predicted
                Pos      Neg
Actual  Pos  [ TP  |  FN ]
        Neg  [ FP  |  TN ]

Precision = TP / (TP + FP)   → "Of all I said Positive, how many were?"
Recall    = TP / (TP + FN)   → "Of all actual Positives, how many did I catch?"
F1        = 2 × (P × R) / (P + R)  → harmonic mean of both
```

### Gotchas & Dev Context
- **Precision vs. Recall tradeoff**: improving one often hurts the other. Adjust the classification threshold.
- **F1** is the default go-to for imbalanced problems, but use **F-beta** if one matters more (`beta>1` weights recall higher).
- A model can have high accuracy + terrible recall (common on imbalanced data).
- Use `classification_report()` in sklearn for a full breakdown per class.

### Production FAQ
**Q: My model has high precision but low recall — what does that mean?**
A: It's conservative — only predicts positive when very confident. It misses many real positives. Lower the decision threshold to catch more.

**Q: Should I optimize F1 or AUC?**
A: F1 at a fixed threshold is useful when you've already chosen the operating point. AUC evaluates performance across all thresholds — better for model comparison.

---

## 18. ROC Curve / AUC

### Definition
The **ROC (Receiver Operating Characteristic) curve** plots True Positive Rate vs. False Positive Rate at every classification threshold. **AUC** (Area Under the Curve) summarizes it as a single number from 0 to 1.

### Real-World Dev Example
Comparing two fraud detection models: Model A has AUC=0.92, Model B has AUC=0.85 → Model A is superior across all thresholds.

### ASCII Diagram
```
TPR (Recall)
1.0 |   ___---
    |  /       ← good model
    | /  ___-- ← random (AUC=0.5)
0.5 |/ --
    |/
  0 +----------> FPR
    0         1.0

AUC = 1.0 → perfect | AUC = 0.5 → random
```

### Gotchas & Dev Context
- AUC is **threshold-independent** — compare models without committing to a cutoff.
- AUC can be **misleading on severely imbalanced data** — use **Precision-Recall AUC (PR-AUC)** instead.
- `roc_auc_score` in sklearn requires probability scores, not hard predictions.
- AUC = 0.5 means your model is no better than flipping a coin.

### Production FAQ
**Q: ROC-AUC is great but my stakeholder needs a binary decision — what do I do?**
A: Choose the threshold that meets your business constraint (e.g., max recalls at 5% false positive rate). Use `precision_recall_curve` or `roc_curve` to find the cutoff point.

**Q: My AUC is 0.97 but the model performs poorly in prod — why?**
A: Possible data leakage in training, distribution shift in production, or you evaluated on the training set by mistake. Always test on a held-out, time-stratified split.

---

## 19. Ensemble Methods (Bagging, Boosting, Stacking)

### Definition
Combining **multiple models** to produce a better prediction than any individual model. The three main strategies are Bagging, Boosting, and Stacking.

### Real-World Dev Example
Kaggle winners routinely use stacking: train XGBoost, LightGBM, and a Neural Net, then train a Logistic Regression on their outputs as the final predictor.

### ASCII Diagram
```
BAGGING:           BOOSTING:          STACKING:
[Tree1]  ←random   [Tree1]            [Model A] ─┐
[Tree2]  ←random   [Tree2] ←corrects  [Model B] ─┤→ [Meta-model] → Output
[Tree3]  ←random   [Tree3] ←corrects  [Model C] ─┘
   ↓                    ↓
Average/Vote      Weighted Sum
(Random Forest)  (XGBoost/LGB)
```

### Gotchas & Dev Context
- **Bagging** reduces variance (overfitting) — good when base models overfit. Random Forest is the canonical example.
- **Boosting** reduces bias (underfitting) — each learner corrects errors of the last. Prone to overfitting without early stopping.
- **Stacking** is the most powerful but most complex — requires careful cross-validation to avoid leakage between layers.
- More models ≠ always better. Ensemble members should be **diverse** (different algorithms or feature sets).

### Production FAQ
**Q: Is stacking worth the engineering complexity in production?**
A: For competitions — yes. For production — only if the performance gain justifies maintaining multiple models. Often a well-tuned single model (LightGBM) is sufficient.

**Q: Bagging vs. Boosting — which is more robust to noisy data?**
A: Bagging — because it averages across models, noise gets diluted. Boosting can amplify noise by focusing on hard-to-classify (possibly mislabeled) examples.

---

*End of Batch 2 — Classical ML Algorithms*
