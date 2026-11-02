# Two-Wheeler Attribute Extraction using Vision-Language Models (VLMs)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Powered by: Google Gemini](https://img.shields.io/badge/VLM-Gemini--3.5--Flash-orange.svg)](https://ai.google.dev/)

An empirical transportation safety and computer vision research framework developed at **IIT Kanpur** to automate the fine-grained extraction of two-wheeler vehicle and rider behavioral attributes from high-speed highway Advanced Traffic Management System (ATMS) camera feeds.

---

## 📌 Project Overview

Two-wheelers account for a disproportionately large share of road traffic fatalities in developing countries like India. Traditional object detectors (e.g., standard YOLO configurations) classify bounding boxes as generic vehicles, often failing to detect subtle behavioral violations such as missing helmets, triple riding, or heavy cargo imbalance.

This project implements a complete zero-shot **Vision-Language Model (VLM)** pipeline utilizing **Google Gemini** to extract 6 safety and behavioral attributes per vehicle:
1. **Vehicle Type:** Motorcycle (Bike) vs. Scooter
2. **Number of Riders:** 1 (Solo), 2 (With Pillion), or 3+ (Triple-riding violation)
3. **Driver Gender:** Male, Female, or Unclear
4. **Driver Helmet Compliance:** Yes (worn on head) vs. No (non-compliant or hanging on bike)
5. **Pillion Helmet Compliance:** Yes, No, or N/A (solo rider)
6. **Luggage / External Load:** None, Backpack (personal body bag), or Cargo/Box (commercial delivery sacks, crates, footboard loads)

---

## 📐 Methodology & Spatial-Temporal Sampling

To validate the VLM against human-level accuracy without spatial or temporal bias, we designed a **Stratified Spatial-Temporal Grid Sampling Plan**:

- **Study Period:** 1 Month (January 2025 ATMS Records, ~162,000 daytime candidates)
- **Spatial Grid:** 9 Highway Camera Locations (SPD001 through SPD010)
- **Temporal Grid:** 11 Daytime Hours (07:00 to 17:59)
- **Sample Distribution:** Exactly 10 random vehicles per (Location x Hour) cell, drawn via round-robin allocation across unique calendar days of the month.
- **Validation Dataset Size:** 9 Locations x 11 Hours x 10 Samples = **990 Ground Truth Images**
- **Statistical Justification:** Aligned with **Cochran's Formula** for large population representative sampling (n ≈ 384 for a 95% confidence level, 5% margin of error).

---

## 📁 Repository Structure

```text
├── sample_dataset.py          # Spatial-temporal stratified grid sampling algorithm
├── run_gemini_benchmark.py    # Automated VLM batch inference pipeline with retry & rate-limiting
├── .env.example               # Template for environment variables (API keys)
├── .gitignore                 # Prevents large images, datasets, and secrets from being committed
└── README.md                  # Project documentation and reproduction guidelines
```

---

## 🚀 Setup & Execution

### 1. Prerequisites
- Python 3.10+
- A Google AI Studio Gemini API Key ([Get free key here](https://aistudio.google.com/))

### 2. Configure API Key
Set your Gemini API key as an environment variable:
```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```
*(Alternatively, copy `.env.example` to `.env` and fill in your key)*.

### 3. Step 1: Extract Stratified Sample
To reproduce the 990-image spatial-temporal sampling from the master ATMS dataset:
```bash
python3 sample_dataset.py
```

### 4. Step 2: Run VLM Batch Inference
To run the automated attribute extraction on the sampled dataset:
```bash
python3 run_gemini_benchmark.py
```
- Includes automatic exponential backoff for HTTP 429 / 503 rate limits.
- Supports **automatic resume**: safely re-runs from where it stopped if interrupted.

---

## 📊 Ground Truth Benchmark Schema

Human annotations and VLM predictions strictly adhere to the following schema:

| Attribute | Valid Classes | Description |
| :--- | :--- | :--- |
| `vehicle_type` | `Motorcycle`, `Scooter` | Visual distinction of step-through scooters vs geared motorcycles |
| `number_of_riders` | `1`, `2`, `3+` | Total human count on vehicle |
| `rider_gender` | `Male`, `Female`, `Unclear` | Apparent gender of primary rider |
| `rider_helmet` | `Yes`, `No` | Protective helmet worn on head |
| `pillion_helmet` | `Yes`, `No`, `N/A` | Pillion helmet compliance |
| `luggage` | `None`, `Backpack`, `Cargo/Box` | Personal bags vs. commercial delivery / footboard cargo |

---

## 👩‍💻 Author & Acknowledgements
- **Author:** Rishika Kumari (Roll No: 230861), IIT Kanpur
- **Supervision:** Department of Civil Engineering, IIT Kanpur
