# EDA Conclusions & Preprocessing Recommendations

> **Project:** Diabetes Prediction  
> **Dataset:** `dataset.csv` (1000 rows, 14 columns)  
> **Sources:** EDA notebooks by Sandra, Omar, Hams, Philo, and Noha  
> **Date:** March 2026

---

## 1. EDA Conclusions

### 1.1 Dataset Overview

| Property | Value |
|---|---|
| Total Records | 1,000 |
| Total Columns | 14 |
| Identifier Columns | `ID`, `No_Pation` |
| Categorical Columns | `Gender`, `CLASS` (target) |
| Numerical Columns | `AGE`, `Urea`, `Cr`, `HbA1c`, `Chol`, `TG`, `HDL`, `LDL`, `VLDL`, `BMI` |
| Missing Values | 0 (none in any column) |
| Exact Duplicate Rows | 0 |
| Content-Based Duplicates | 341 (when excluding `ID` and `No_Pation`) |

### 1.2 Data Quality Issues

#### Gender Column — Inconsistent Casing
The `Gender` column contains three unique values: `'F'`, `'M'`, and `'f'` (lowercase). The lowercase `'f'` is clearly a data entry inconsistency and should be normalized to `'F'`.

#### CLASS Column — Trailing Whitespace
The target column `CLASS` contains five unique values instead of the expected three:

| Raw Value | Intended Value | Count |
|---|---|---|
| `'Y'` | Diabetic | ~840 |
| `'Y '` (trailing space) | Diabetic | ~4 |
| `'N'` | Non-Diabetic | ~100 |
| `'N '` (trailing space) | Non-Diabetic | ~3 |
| `'P'` | Pre-Diabetic | 53 |

The trailing whitespace in `'Y '` and `'N '` must be stripped to produce clean class labels.

#### Medically Impossible / Extreme Values
- **Cholesterol (`Chol`) min = 0.0:** A living person cannot have zero cholesterol. This is either a data entry error or a missing value encoded as 0.
- **Creatinine (`Cr`) max = 800:** The IQR range is 48–73. A value of 800 is an extreme outlier, likely a data entry error (possibly missing a decimal point).
- **VLDL max = 35.0:** The IQR range is 0.7–1.5. This extreme value is suspicious.
- **Urea max = 38.9:** The IQR range is 3.7–5.7. While high urea can occur in kidney disease, this warrants investigation.

### 1.3 Target Variable — Severe Class Imbalance

| Class | Label | Count | Percentage |
|---|---|---|---|
| Y | Diabetic | 844 | 84.4% |
| N | Non-Diabetic | 103 | 10.3% |
| P | Pre-Diabetic | 53 | 5.3% |

**This is a critically imbalanced dataset.** The dominant class (Diabetic) is 16× larger than Pre-Diabetic. A naive classifier predicting "Y" for everything would achieve 84.4% accuracy, making accuracy a misleading metric. The minority classes (N and P) will be very difficult for models to learn without intervention.

### 1.4 Feature Importance (ANOVA Test Results)

Sandra's notebook performed one-way ANOVA tests for each numerical feature across the three classes. Results:

| Feature | Statistically Significant (p < 0.05) | Interpretation |
|---|---|---|
| **HbA1c** | Yes | Strongest separator between classes |
| **BMI** | Yes | Strong separator |
| **AGE** | Yes | Strong separator |
| **Chol** | Yes | Moderate separator |
| **TG** | Yes | Moderate separator |
| **VLDL** | Yes | Moderate separator |
| Urea | No | Not a significant predictor |
| Cr | No | Not a significant predictor |
| HDL | No | Not a significant predictor |
| LDL | No | Not a significant predictor |

### 1.5 Best Separating Features (Mean Values by Class)

| Feature | N (Non-Diabetic) | P (Pre-Diabetic) | Y (Diabetic) | Separation Quality |
|---|---|---|---|---|
| **HbA1c** | 4.56 | 6.00 | 8.88 | Excellent — clear linear progression |
| **BMI** | 22.37 | 23.93 | 30.81 | Excellent — large gap between N/P and Y |
| **AGE** | 44.23 | 43.28 | 55.31 | Good — Y patients are notably older |
| Chol | 4.32 | 4.30 | 4.92 | Moderate |
| TG | 1.32 | 1.56 | 2.20 | Moderate |

**Visual confirmation:** Boxplots across all notebooks show clear separation in HbA1c and BMI distributions by class. Scatter plots of BMI vs HbA1c show distinct clustering by class. KDE plots show minimal overlap in BMI distributions between N and Y classes.

### 1.6 Outlier Analysis (IQR Method)

| Feature | Outlier Count | Percentage | Notable Extremes |
|---|---|---|---|
| AGE | 98 | 9.8% | Young patients (< 30) are rare |
| VLDL | 74 | 7.4% | Max = 35.0 (IQR: 0.7–1.5) |
| Urea | 65 | 6.5% | Max = 38.9 (IQR: 3.7–5.7) |
| TG | 55 | 5.5% | Max = 13.8 |
| Cr | 52 | 5.2% | Max = 800 (IQR: 48–73) — extreme |
| HDL | 50 | 5.0% | Max = 9.9 |
| Chol | 27 | 2.7% | Min = 0.0 (impossible) |
| LDL | 11 | 1.1% | Relatively few |
| HbA1c | 6 | 0.6% | Very few |
| BMI | 3 | 0.3% | Very few |

**Important caveat:** In medical datasets, statistical outliers often represent critically ill patients (e.g., very high creatinine = kidney failure, very high HbA1c = uncontrolled diabetes). Blindly removing outliers would discard clinically meaningful data. Only clearly erroneous values (Chol = 0, Cr = 800) should be treated as errors.

### 1.7 Correlation Analysis

**Top correlated feature pairs:**

| Feature Pair | Correlation (r) | Concern |
|---|---|---|
| Urea ↔ Cr | 0.624 | **Multicollinearity risk** — both measure kidney function |
| LDL ↔ Chol | 0.417 | Moderate — LDL is a component of total Chol |
| BMI ↔ HbA1c | 0.413 | Expected — obesity linked to diabetes |
| HbA1c ↔ AGE | 0.379 | Expected — diabetes prevalence increases with age |
| BMI ↔ AGE | 0.376 | Expected — BMI tends to increase with age |
| TG ↔ Chol | 0.322 | Moderate — both are lipid measures |

**Key concern:** The Urea–Cr correlation (0.624) is the strongest in the dataset and both are statistically non-significant predictors. This suggests they carry redundant, non-useful information. Additionally, LDL is mathematically derived from Chol, TG, and HDL (Friedewald equation), creating inherent collinearity.

### 1.8 Distribution Characteristics

| Feature | Skewness | Distribution Shape |
|---|---|---|
| Urea | Right-skewed | Heavy positive tail |
| Cr | Right-skewed | Heavy positive tail, extreme outliers |
| TG | Right-skewed | Heavy positive tail |
| VLDL | Right-skewed | Heavy positive tail |
| AGE | Left-skewed | Most patients are older |
| HbA1c | Roughly normal | Slight right skew due to diabetic majority |
| BMI | Roughly normal | Slight right skew |
| Chol | Roughly normal | — |
| HDL | Roughly normal | — |
| LDL | Roughly normal | — |

**Scale differences:** Features have vastly different scales. For example, Cr ranges from 6 to 800 while HDL ranges from 0.2 to 9.9. This will heavily bias distance-based and gradient-based algorithms.

### 1.9 Gender Analysis

| Gender | Count | Percentage | Diabetic Rate |
|---|---|---|---|
| Male (M) | 565 | 56.5% | 86.7% |
| Female (F) | 435 | 43.5% | 81.4% |

Males have a slightly higher diabetic rate (86.7% vs 81.4%), but the difference is moderate. The dataset has a mild male skew.

### 1.10 Age Analysis

| Age Group | Diabetic Rate |
|---|---|
| < 30 | 55.6% |
| 30–45 | 44.4% |
| 45–60 | 89.8% |
| 60+ | 98.0% |

Diabetic prevalence increases dramatically with age. Nearly all patients aged 60+ are diabetic. The 30–45 group has a lower rate than < 30, which may reflect sampling bias or the small sample sizes in younger groups.

### 1.11 BMI and Diabetes Relationship

From Philo's analysis using WHO BMI categories:

- **All Non-Diabetic (N) patients have Normal BMI (< 25).** Zero Non-Diabetic patients are Overweight or Obese.
- **526 patients are Obese (BMI ≥ 30),** and 523 of them (99.4%) are Diabetic.
- This makes BMI one of the most decisive features, almost perfectly separating N from Y.

### 1.12 Content-Based Duplicates

Omar's analysis found **341 content-based duplicate rows** when excluding the `ID` and `No_Pation` columns. This means 34.1% of the dataset consists of rows with identical medical measurements and outcomes. These may be:
- True duplicates (same patient recorded multiple times)
- Different patients with coincidentally identical measurements (less likely with continuous values)

This is a significant concern for model training, as duplicates can inflate performance during cross-validation if the same data appears in both train and test splits.

### 1.13 Identifier Columns

`ID` and `No_Pation` are patient identifiers with no predictive value. They are purely administrative columns.

---

## 2. Preprocessing Recommendations

### 2.1 Drop Identifier Columns

**Action:** Remove `ID` and `No_Pation` columns.

```python
df.drop(columns=['ID', 'No_Pation'], inplace=True)
```

**Reason:** These are administrative identifiers that carry zero predictive information. If left in, models may overfit to arbitrary ID patterns.

### 2.2 Clean Text Values

#### Strip whitespace from CLASS column

**Action:** Strip all leading/trailing whitespace from the `CLASS` column.

```python
df['CLASS'] = df['CLASS'].str.strip()
```

This reduces the 5 unique values (`'N'`, `'N '`, `'P'`, `'Y'`, `'Y '`) to the correct 3 (`'N'`, `'P'`, `'Y'`).

#### Normalize Gender casing

**Action:** Convert all Gender values to uppercase.

```python
df['Gender'] = df['Gender'].str.upper()
```

This merges `'f'` into `'F'`, producing only `'F'` and `'M'`.

### 2.3 Handle Content-Based Duplicates

**Action:** Remove content-based duplicate rows (keeping the first occurrence).

```python
feature_cols = [col for col in df.columns if col not in ['ID', 'No_Pation']]
df.drop_duplicates(subset=feature_cols, keep='first', inplace=True)
```

**Reason:** 341 content-based duplicates (34.1%) can cause data leakage during train-test splitting. If duplicates appear in both train and test sets, the model's generalization performance will be overestimated. Remove them **after** dropping `ID`/`No_Pation` but **before** any splitting or resampling.

**Note:** After deduplication, re-check class distribution as this may worsen the imbalance.

### 2.4 Handle Erroneous / Impossible Values

#### Cholesterol = 0

**Action:** Replace `Chol == 0` with `NaN`, then impute.

```python
import numpy as np
df.loc[df['Chol'] == 0, 'Chol'] = np.nan
# Impute with class-conditional median
df['Chol'] = df.groupby('CLASS')['Chol'].transform(
    lambda x: x.fillna(x.median())
)
```

**Reason:** Zero cholesterol is biologically impossible. Using class-conditional median preserves the relationship between cholesterol levels and diabetes status.

#### Creatinine = 800

**Action:** Investigate and likely cap or replace.

```python
# Option A: Replace extreme Cr values with NaN and impute
cr_upper = df['Cr'].quantile(0.99)
df.loc[df['Cr'] > cr_upper, 'Cr'] = np.nan
df['Cr'] = df.groupby('CLASS')['Cr'].transform(
    lambda x: x.fillna(x.median())
)

# Option B: Winsorize at the 99th percentile
from scipy.stats.mstats import winsorize
df['Cr'] = winsorize(df['Cr'], limits=[0, 0.01])
```

**Reason:** A Cr value of 800 with an IQR of 48–73 is almost certainly a data entry error. Even in severe kidney failure, creatinine values rarely exceed 15 mg/dL (or ~1300 µmol/L, depending on units).

### 2.5 Outlier Handling Strategy

**Action:** Use a conservative, domain-aware approach — do NOT remove outliers blindly.

**Recommended strategy:**

1. **Clearly erroneous values** (Chol = 0, Cr = 800): Replace with NaN and impute (see 2.4).
2. **Extreme but plausible outliers** (high Urea, VLDL, TG): Apply **Winsorization** (capping at the 1st and 99th percentiles) rather than removal.
   ```python
   from scipy.stats.mstats import winsorize
   for col in ['Urea', 'Cr', 'TG', 'VLDL', 'HDL']:
       df[col] = winsorize(df[col], limits=[0.01, 0.01])
   ```
3. **Statistically outlying but medically meaningful values** (high HbA1c, high BMI, young patients): **Keep as-is.** These represent real clinical variation.

**Reason:** In medical data, outliers often represent the most critically ill patients — exactly the cases the model needs to learn to identify. Aggressive outlier removal would disproportionately affect the minority classes, worsening an already severe imbalance.

### 2.6 Handle Skewed Distributions

**Action:** Apply log transformation to right-skewed features.

```python
import numpy as np
skewed_features = ['Urea', 'Cr', 'TG', 'VLDL']
for col in skewed_features:
    df[col] = np.log1p(df[col])  # log(1 + x) to handle zeros safely
```

**Reason:** Urea, Cr, TG, and VLDL all exhibit heavy right skew (confirmed by histograms across all notebooks, and Hams's explicit log transformation analysis). Log transformation reduces the influence of extreme values and makes distributions more symmetric, which benefits many algorithms (linear models, KNN, SVMs). Tree-based models (Random Forest, XGBoost) are invariant to monotonic transformations, so this step is optional for those.

**Note:** Apply this **after** outlier handling and **before** scaling.

### 2.7 Encode Categorical Variables

#### Gender — Binary Encoding

**Action:** Map Gender to a numeric binary column.

```python
df['Gender'] = df['Gender'].map({'M': 1, 'F': 0})
```

Or use Label Encoding. Since Gender is binary, one-hot encoding is unnecessary (it would create a redundant column).

#### CLASS (Target) — Label Encoding

**Action:** Encode the target variable as integers.

```python
# Option A: Simple mapping (preserves clinical ordering)
class_map = {'N': 0, 'P': 1, 'Y': 2}
df['CLASS'] = df['CLASS'].map(class_map)

# Option B: Using LabelEncoder
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
df['CLASS'] = le.fit_transform(df['CLASS'])
```

**Note:** If treating this as a binary classification problem (Diabetic vs Non-Diabetic), consider merging Pre-Diabetic (P) with either N or Y, or removing P entirely. This decision should be based on the project's clinical objectives.

### 2.8 Feature Scaling

**Action:** Scale all numerical features to a common range.

```python
from sklearn.preprocessing import StandardScaler  # or MinMaxScaler

scaler = StandardScaler()
numerical_cols = ['AGE', 'Urea', 'Cr', 'HbA1c', 'Chol', 'TG', 'HDL', 'LDL', 'VLDL', 'BMI']
df[numerical_cols] = scaler.fit_transform(df[numerical_cols])
```

**Reason:** Features have vastly different scales (e.g., Cr: 6–800 vs HDL: 0.2–9.9). Distance-based algorithms (KNN, SVM) and gradient-based algorithms (Logistic Regression, Neural Networks) are sensitive to feature scale. Tree-based models are not affected but scaling does no harm.

**Important:** Fit the scaler on the **training set only**, then transform both train and test sets to prevent data leakage.

### 2.9 Handle Class Imbalance

This is the most critical preprocessing step. With an 84.4% / 10.3% / 5.3% split, the minority classes will be severely underlearned without intervention.

**Recommended approaches (use one or combine):**

#### Option A: SMOTE (Synthetic Minority Over-sampling)
```python
from imblearn.over_sampling import SMOTE

smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
```
Generates synthetic samples for the minority classes (N and P) by interpolating between existing samples.

#### Option B: Class Weights
```python
# For sklearn classifiers
model = RandomForestClassifier(class_weight='balanced', random_state=42)
```
Penalizes misclassification of minority classes more heavily. No synthetic data generated.

#### Option C: Hybrid — SMOTE + Tomek Links
```python
from imblearn.combine import SMOTETomek

smt = SMOTETomek(random_state=42)
X_resampled, y_resampled = smt.fit_resample(X_train, y_train)
```
Over-samples minority classes with SMOTE, then removes ambiguous borderline samples with Tomek links.

**Critical:** Apply resampling **only to the training set**, never to the test/validation set. The test set must reflect the true data distribution.

**Evaluation metrics:** Do NOT rely on accuracy. Use:
- **Macro-averaged F1-score** (equal weight to each class)
- **Per-class precision and recall** (especially for N and P)
- **Confusion matrix** (to visualize misclassification patterns)
- **ROC-AUC** (one-vs-rest for multiclass)

### 2.10 Consider Dropping Non-Significant Features

Based on the ANOVA results, four features are NOT statistically significant: **Urea, Cr, HDL, LDL**.

**Recommendation:** Do not drop them outright during preprocessing. Instead:

1. Train a baseline model with all features.
2. Train a second model without Urea, Cr, HDL, and LDL.
3. Compare performance. If the reduced model performs equally well (or better due to reduced noise), keep the reduced feature set.

**Additional consideration:** Urea and Cr have a strong correlation (0.624). If both are kept, consider dropping one to reduce multicollinearity, especially for linear models. Similarly, LDL is mathematically derived from Chol, TG, and HDL (Friedewald equation: LDL = Chol − HDL − TG/5), creating inherent redundancy.

### 2.11 Potential Feature Engineering

Based on findings from all notebooks (especially Philo's medical ratio explorations):

| New Feature | Formula | Clinical Rationale |
|---|---|---|
| `BMI_HbA1c_interaction` | `BMI × HbA1c` | Captures joint effect of obesity and glucose control |
| `TG_HDL_ratio` | `TG / HDL` | Established marker of insulin resistance |
| `Chol_HDL_ratio` | `Chol / HDL` | Cardiovascular risk indicator |
| `LDL_HDL_ratio` | `LDL / HDL` | Atherogenic index |
| `Age_Group` | Binned AGE | Captures non-linear age effect (e.g., <30, 30–45, 45–60, 60+) |
| `BMI_Category` | WHO BMI bins | Normal (<25), Overweight (25–30), Obese (≥30) |

**Note:** Feature engineering should be validated through cross-validation. Only keep engineered features that improve model performance.

### 2.12 Train-Test Splitting

**Action:** Split the data using stratified sampling to preserve class proportions.

```python
from sklearn.model_selection import train_test_split

X = df.drop(columns=['CLASS'])
y = df['CLASS']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
```

**Critical considerations:**
- **Stratify by CLASS** to ensure the 84.4/10.3/5.3 ratio is preserved in both train and test sets. Without stratification, the test set may have zero Pre-Diabetic samples.
- **Split BEFORE any resampling** (SMOTE, etc.) to prevent data leakage.
- **Split AFTER duplicate removal** to prevent the same patient from appearing in both sets.
- **Fit scalers/encoders on training data only**, then transform the test set.
- Consider using **Stratified K-Fold Cross-Validation** (k=5 or k=10) instead of a single split, given the small dataset size (especially after deduplication, which reduces it to ~659 rows).

---

## Summary: Recommended Preprocessing Pipeline Order

```
1.  Drop columns: ID, No_Pation
2.  Clean text: strip whitespace from CLASS, uppercase Gender
3.  Remove content-based duplicates
4.  Fix erroneous values: Chol=0 → NaN, Cr=800 → NaN, then impute
5.  Winsorize extreme outliers (Urea, Cr, TG, VLDL, HDL at 1st/99th percentile)
6.  Train-test split (stratified by CLASS, 80/20)
7.  Log-transform skewed features (Urea, Cr, TG, VLDL) — fit on train only
8.  Encode categoricals (Gender → binary, CLASS → integer labels)
9.  Scale numerical features (StandardScaler) — fit on train only
10. Handle class imbalance (SMOTE or class weights) — on train set only
11. (Optional) Feature engineering — validate via cross-validation
12. (Optional) Feature selection — compare full vs reduced feature sets
```

> **Note:** Steps 7–10 must be applied **only after splitting** to prevent data leakage. The scaler, encoder, and SMOTE must be fit exclusively on the training set.
