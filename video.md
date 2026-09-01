# DisputeShield — 5-Minute Demo Video Pitch Script

> **Target Duration:** Exactly 4:30 – 5:00 minutes  
> **Track:** Track 02 — AI Risk Manager (Razorpay AI Buildathon 2026)  
> **Speaker:** Anurag  
> **Format:** Screen Recording + Webcam In Corner (e.g. Loom, OBS, Screen Studio)

---

## 🛠️ Recording Setup Checklist

Before pressing Record, ensure the following tabs / windows are open:
1. **Window 1 (Browser):** Next.js UI running at `http://localhost:3000` (open to Dashboard tab).
2. **Window 2 (Terminal):** Terminal in `Razorpay/` with virtual environment activated.
3. **Window 3 (GitHub):** Repository page `https://github.com/anur1g5473/Razorpay`.

---

## ⏱️ Timeline & Scene Overview

| Time | Scene / Action | Focus Topic |
|---|---|---|
| **0:00 – 0:45** | Slide / Dashboard Hero | The $100B+ Chargeback Dilemma & Merchant Pain Points |
| **0:45 – 1:30** | System Diagram / ARCHITECTURE.md | Core Architecture: Deterministic Scorer + Abstention Gate + Fact Drafter |
| **1:30 – 2:45** | Live Demo (Dashboard & CLI) | Winning Case Walkthrough (`disp_001` - 3DS ECI 05 Fraud Dispute) |
| **2:45 – 3:45** | Live Demo (Abstention Gate) | Graceful Failure & Honest Abstention (`disp_081` - Retry Discrepancy) |
| **3:45 – 4:30** | Evaluation View / Terminal Eval | 100-Case Benchmark, 90% Accuracy, 100% Recall, ₹413K Net Gain |
| **4:30 – 5:00** | GitHub Repo & Conclusion | Summary, Defense-Only Guardrails, Ready-to-deploy Open Source |

---

## 🎙️ Detailed Voiceover Script

### Segment 1: The Problem (0:00 – 0:45)
**Visual:** Show Next.js Dashboard Hero (`http://localhost:3000`) or introductory title slide.

> *"Hello everyone! I'm Anurag, and today I'm excited to present **DisputeShield** for Track 02: AI Risk Manager at the Razorpay AI Buildathon 2026.*
> 
> *Every year, online businesses lose billions in revenue to chargebacks and payment disputes. When a customer files a dispute with their issuing bank claiming unauthorized payment or missing delivery, the card network starts a countdown clock—giving merchants under 14 days to assemble a compelling, formal evidence pack.*
> 
> *Merchants are trapped between two bad options: spend hours manually digging through 3DS logs, courier telemetry, and order invoices, or use naive automation tools that blindly contest everything—burning ₹1,500 to ₹4,000 in scheme penalty fees on unwinnable disputes.*
> 
> *DisputeShield solves this: an autonomous, defense-only AI Risk Manager that scores dispute evidence against card network rubrics, drafts bank-ready rebuttal letters, and honestly knows when to abstain."*

---

### Segment 2: System Architecture (0:45 – 1:30)
**Visual:** Switch to Architecture tab or show `ARCHITECTURE.md`.

> *"Let's look at how DisputeShield works under the hood.*
> 
> *When a dispute webhook arrives from Razorpay or the card networks, our pipeline executes 4 precise stages:*
> 1. **Evidence Retrieval:** Pulls structured transaction metadata, 3DS authentication tokens, courier tracking, customer communications, and terms acceptance logs.
> 2. **Deterministic Rubric Scorer:** Evaluates the evidence against network-compliant scoring schemas covering Visa, Mastercard, RuPay, Amex, and NPCI UPI reason codes. Unlike black-box LLMs, our scoring is 100% reproducible and explainable.
> 3. **The Honest Abstention Gate:** Identifies unwinnable or ambiguous cases—such as Return-To-Origin packages or missing 3DS authentication—and proactively flags them to concede, preventing expensive representation fines.
> 4. **Fact-Grounded LLM Response Drafter:** For winnable disputes, Google Gemini drafts a formal legal rebuttal letter citing strictly verified telemetry and card network liability-shift rules."*



---

### Segment 3: Live Demo — Winning Dispute (1:30 – 2:45)
**Visual:** Switch to Dashboard Analyze Tab / Terminal (`python -m agent analyze disp_001`).

> *"Now let's see a live demonstration.*
> 
> *Here is case `disp_001`: a ₹1,612 fraud dispute under reason code UPI-01.*
> 
> *When we trigger analysis, in under 15 milliseconds, the system evaluates all evidence:*
> - *Full 3DS V2 authentication confirmed with ECI indicator 05: +35 points.*
> - *IP geo-match with no proxy/VPN: +20 points.*
> - *Support interaction history and 14 prior successful orders on record: +35 points.*
> - *Terms acceptance at checkout: +10 points.*
> 
> *Total score: 100/100, yielding a 95% win probability and a definitive **CONTEST** recommendation.*
> 
> *And look at the generated formal rebuttal letter below: it accurately references the transaction ID, cardholder identity, exact timestamps, and explicitly cites the issuing bank liability shift protocol under 3D Secure rules. No hallucinations, no generic boilerplate—ready to submit to the bank in seconds."*

---

### Segment 4: Graceful Failure & Honest Abstention (2:45 – 3:45)
**Visual:** Show case `disp_081` in Dashboard or run `python -m agent analyze disp_081`.

> *"Now, let's explore our key differentiator: **Graceful Failure and Honest Abstention**.*
> 
> *In case `disp_081`, the customer disputed a duplicate payment of ₹1,308.*
> 
> *Most naive AI tools see an invoice and immediately recommend contesting. But DisputeShield's Abstention Gate inspected the payment gateway logs and detected an automated retry discrepancy with missing dispatch manifests.*
> 
> *The system flagged an immediate abstention trigger: 'Gateway logs confirm automated payment retry discrepancy.'*
> 
> *Instead of risking a ₹1,500 scheme arbitration penalty fee on a losing dispute, DisputeShield automatically recommended **ABSTAIN**.*
> 
> *By knowing when NOT to fight, DisputeShield protects both merchant profitability and their acquiring risk score."*

---

### Segment 5: Benchmark Evaluation & Financial ROI (3:45 – 4:30)
**Visual:** Switch to Evaluation Hub tab or run `python -m agent eval` in terminal.

> *"We validated DisputeShield across a rigorous 100-case held-out benchmark with a balanced 40 win, 40 lose, and 20 ambiguous case distribution across card schemes and UPI.*
> 
> *Here are our un-cherry-picked benchmark results:*
> - **Overall Accuracy:** 90.0%
> - **Contest Recall:** 100.0% (captured 100% of all winnable disputed volume)
> - **Gross Recovered Volume:** ₹360,702 recovered
> - **Prevented Scheme Penalties:** ₹60,000 saved by conceding unwinnable cases
> - **Net Financial Gain:** ₹413,202 across ₹1.13M disputed volume
> - **Sub-Millisecond Speed:** Mean deterministic scoring latency of 0.06 ms*
> 
> *Every single one of our 56 automated unit and integration tests passes in our CI/CD workflow."*

---

### Segment 6: Conclusion (4:30 – 5:00)
**Visual:** Switch to GitHub repo `anur1g5473/Razorpay`.

> *"In conclusion, DisputeShield delivers a complete, defense-only AI Risk Manager that turns chargebacks from an administrative headache into an automated, financially optimal defense system.*
> 
> *Everything is fully documented, strictly defense-only, and ready to deploy.*
> 
> *Thank you very much for your time, and thank you to the Razorpay team!"*

---
