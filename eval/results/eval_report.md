# DisputeShield — Benchmark Evaluation Report

> **Evaluation Run ID:** `eval_20260901_100747`  
> **Date:** 2026-09-01T10:07:47.078380+00:00  
> **Total Evaluated Cases:** 100

## 1. Executive Summary & Core Metrics

| Metric | Value | Benchmark Target | Status |
|---|---|---|---|
| **Overall Accuracy** | **90.0%** | > 85.0% | PASS |
| **Contest Precision** | **80.0%** | > 90.0% | REVIEW |
| **Contest Recall** | **100.0%** | > 85.0% | PASS |
| **Macro F1 Score** | **0.8519** | > 0.8500 | PASS |
| **P95 Latency** | **0.1 ms** | < 250 ms | PASS |

## 2. Confusion Matrix

| Ground Truth \ Recommendation | Contest (Win) | Accept (Concede) | Human Review (Abstain) |
|---|---|---|---|
| **Actual WIN** (40 cases) | **40** | 0 | 0 |
| **Actual LOSE** (40 cases) | 0 | **40** | 0 |
| **Actual AMBIGUOUS** (20 cases) | 10 | 0 | **10** |

## 3. Financial Cost & ROI Analysis

- **Total Disputed Volume:** INR 1,130,765.93
- **Direct Recovered Amount:** INR 360,702.22 (100.0% of winnable volume)
- **Prevented Representation Penalties:** INR 60,000.00
- **False Contest Penalty Incurred:** INR 7,500.00
- **Net Financial Gain:** **INR 413,202.22**
- **Savings vs Blind Automated Contest:** **INR 52,500.00**

## 4. Category Performance Breakdown

| Category | Total Cases | Accuracy | Macro F1 | Net Financial Gain |
|---|---|---|---|---|
| Fraudulent / Unauthorized Transaction | 20 | 100.0% | 1.0000 | INR 107,057.33 |
| Product or Service Not Received | 20 | 80.0% | 0.6000 | INR 74,734.48 |
| Product Unacceptable, Defective, or Not as Described | 16 | 100.0% | 1.0000 | INR 88,750.00 |
| Credit or Refund Not Processed | 16 | 75.0% | 0.5833 | INR 72,902.69 |
| Duplicate Processing or Incorrect Amount | 14 | 85.7% | 0.6190 | INR 46,263.72 |
| Cancelled Subscription / Recurring Charge | 14 | 100.0% | 1.0000 | INR 23,494.00 |

## 5. Performance Latency Profile

- **Mean Latency:** 0.07 ms
- **Median (P50):** 0.06 ms
- **P95 Latency:** 0.11 ms
- **Min / Max:** 0.04 ms / 0.2 ms