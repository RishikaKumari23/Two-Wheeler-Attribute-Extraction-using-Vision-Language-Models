# 🏍️ VLM Validation Benchmark Evaluation Report (N = 990)

**Model:** Google Gemini (Zero-Shot with Structured JSON Context)
**Ground Truth:** Human-labeled dataset (990 stratified highway frames)

## 🏆 Executive Summary: Macro Performance

| Attribute | Overall Accuracy | Macro F1-Score | Evaluated Sample Size (N) | Evaluation Status |
| :--- | :---: | :---: | :---: | :---: |
| **Vehicle Type (Motorcycle vs Scooter)** | **99.49%** | **99.30%** | 974 | 🌟 Exceptional (>95%) |
| **Rider Helmet Compliance (Driver)** | **97.19%** | **97.11%** | 924 | 🌟 Exceptional (>95%) |
| **Number of Riders (Solo, Double, Triple)** | **93.11%** | **86.35%** | 972 | ✅ High (>90%) |
| **Pillion Helmet Compliance** | **95.64%** | **82.11%** | 941 | 🌟 Exceptional (>95%) |
| **Rider Gender** | **97.22%** | **74.40%** | 970 | 🌟 Exceptional (>95%) |
| **Luggage / Cargo Detection** | **80.02%** | **67.68%** | 961 | ⚠️ Moderate (~80%) |

---

## 🔍 Detailed Class-Level Performance

### 📌 Vehicle Type (Motorcycle vs Scooter)
- **Overall Accuracy:** 99.49%
- **Macro F1-Score:** 99.30%

| Class | Support (Ground Truth) | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| **Motorcycle** | 740 | 99.7% | 99.6% | 99.7% |
| **Scooter** | 234 | 98.7% | 99.1% | 98.9% |

### 📌 Rider Helmet Compliance (Driver)
- **Overall Accuracy:** 97.19%
- **Macro F1-Score:** 97.11%

| Class | Support (Ground Truth) | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| **No** | 389 | 96.9% | 96.4% | 96.6% |
| **Yes** | 535 | 97.4% | 97.8% | 97.6% |

### 📌 Number of Riders (Solo, Double, Triple)
- **Overall Accuracy:** 93.11%
- **Macro F1-Score:** 86.35%

| Class | Support (Ground Truth) | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| **1** | 556 | 94.3% | 98.2% | 96.2% |
| **2** | 365 | 91.6% | 89.9% | 90.7% |
| **3+** | 51 | 88.6% | 60.8% | 72.1% |

### 📌 Pillion Helmet Compliance
- **Overall Accuracy:** 95.64%
- **Macro F1-Score:** 82.11%

| Class | Support (Ground Truth) | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| **N/A** | 553 | 95.6% | 98.6% | 97.1% |
| **No** | 378 | 97.2% | 92.3% | 94.7% |
| **Yes** | 10 | 50.0% | 60.0% | 54.5% |

### 📌 Rider Gender
- **Overall Accuracy:** 97.22%
- **Macro F1-Score:** 74.40%

| Class | Support (Ground Truth) | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| **Female** | 24 | 100.0% | 75.0% | 85.7% |
| **Male** | 932 | 98.7% | 98.5% | 98.6% |
| **Unclear** | 14 | 31.8% | 50.0% | 38.9% |

### 📌 Luggage / Cargo Detection
- **Overall Accuracy:** 80.02%
- **Macro F1-Score:** 67.68%

| Class | Support (Ground Truth) | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| **Backpack** | 138 | 68.4% | 58.0% | 62.7% |
| **Cargo/Box** | 158 | 74.4% | 40.5% | 52.5% |
| **None** | 665 | 82.5% | 94.0% | 87.8% |
