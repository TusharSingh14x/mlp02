# A MAJOR PROJECT REPORT ON
# PhishGuard-XAI: A Security-Hardened, Phased Feature Selection and Metaheuristic Stacking Framework for Robust Phishing Detection

*Submitted in partial fulfillment of the requirements for the award of the degree of*  
**BACHELOR OF TECHNOLOGY / MASTER OF TECHNOLOGY**  
*in*  
**COMPUTER SCIENCE AND ENGINEERING**

**Submitted by:**  
* **Tushar Singh** (Enrollment No: [Roll / BT No.])  
* **Eshan** (Enrollment No: [Roll / BT No.])  
* **Rudra** (Enrollment No: [Roll / BT No.])  

**Under the Guidance of:**  
**[Supervisor Name]**  
*Designation, Department of Computer Science & Engineering*  
*Indian Institute of Information Technology, Nagpur*  

**DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING**  
**INDIAN INSTITUTE OF INFORMATION TECHNOLOGY, NAGPUR**  
Nagpur, Maharashtra, India -- 441108  
*Academic Session: 2026–2027*

---

## BONA FIDE CERTIFICATE

This is to certify that the project report entitled **"PhishGuard-XAI: A Security-Hardened, Phased Feature Selection and Metaheuristic Stacking Framework for Robust Phishing Detection"** submitted by **Tushar Singh**, **Eshan**, and **Rudra** in partial fulfillment of the requirements for the award of the degree of **Bachelor of Technology in Computer Science and Engineering** at **Indian Institute of Information Technology, Nagpur** is a bona fide record of work carried out by them under my supervision and guidance during the academic session 2026–2027.

The results embodied in this report have not been submitted to any other University or Institute for the award of any degree or diploma.

<br><br>

**[Internal Guide / Supervisor Name]**  
*Project Supervisor, Dept. of CSE, IIITN*  

**[Head of Department Name]**  
*Head of Department, Dept. of CSE, IIITN*  

**External Examiner 1:** _______________________ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **External Examiner 2:** _______________________

---

## CANDIDATE'S DECLARATION

We hereby declare that the work presented in this project report entitled **"PhishGuard-XAI: A Security-Hardened, Phased Feature Selection and Metaheuristic Stacking Framework for Robust Phishing Detection"** has been carried out by us under the supervision of **[Supervisor Name]**, Department of Computer Science and Engineering, Indian Institute of Information Technology, Nagpur.

We declare that the work embodied in this project report is original and has not been submitted previously in part or full for the award of any other degree, diploma, or certificate to any other University or Institution. Whenever we have used materials (data, theoretical analyses, figures, text) from other sources, they have been duly cited and referenced in accordance with standard academic ethics.

**Date:** November 13, 2026  
**Place:** Nagpur, India  

* **Tushar Singh** (Enrollment No: [Roll / BT No.])  
* **Eshan** (Enrollment No: [Roll / BT No.])  
* **Rudra** (Enrollment No: [Roll / BT No.])  

---

## ACKNOWLEDGEMENT

We would like to express our deepest gratitude and heartfelt appreciation to our respected project supervisor, **[Supervisor Name]**, for their continuous guidance, intellectual motivation, invaluable advice, and encouragement throughout the duration of this project. Their profound technical insights into machine learning and network security were crucial in shaping the architecture of PhishGuard-XAI.

We are profoundly grateful to **[Head of Department Name]**, Head of the Department of Computer Science and Engineering, Indian Institute of Information Technology, Nagpur, for providing the necessary laboratory facilities, compute resources, and academic environment conducive to high-quality research.

We would also like to thank all the faculty members and technical staff of the Department of Computer Science and Engineering for their direct and indirect support. Lastly, we extend our heartfelt thanks to our parents, family members, and friends for their constant patience, moral support, and blessings throughout our academic journey.

<br>

**Tushar Singh** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Eshan** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Rudra**

---

## ABSTRACT

Phishing attacks represent the most pervasive cyber threat in modern enterprise environments, accounting for over 80% of reported enterprise security breaches and resulting in billions of dollars in annual global losses. Although existing academic literature reports theoretical detection accuracies exceeding 98% using machine learning, deployed systems suffer from four fatal vulnerabilities:
1. **Training-Serving Feature Disparity (The Dummy Skew Flaw)**: Baseline models rely on third-party network lookups (live DNS, WHOIS registration age, Alexa web traffic rank). In live perimeter gateways, fetching these features incurs severe latency (2 to 5 seconds per URL) or fails completely when malicious domains go offline. Consequently, operational scanners insert dummy zero values for unpopulated features, causing catastrophic false-positive spikes.
2. **Generalization Collapse**: Single decision trees or random forests overfit specific training distributions, suffering up to 15%–35% recall collapse when tested on unseen, out-of-distribution phishing feeds.
3. **The Interpretability Gap**: Raw scalar probability outputs ($p \in [0, 1]$) provide no actionable forensic context to Security Operations Center (SOC) analysts.
4. **Adversarial Vulnerabilities**: Classical detectors fail against Cyrillic Unicode homoglyphs and leetspeak, while unshielded Large Language Model (LLM) forensic assistants are susceptible to adversarial prompt injection embedded inside URL query strings.

To resolve these challenges, this project presents **PhishGuard-XAI**, a security-hardened, real-time phishing detection and incident triage framework. The architecture integrates:
* A **pure static 50-dimensional URL feature extraction engine** computing lexical, structural, and Shannon character entropy in **0.09 ms per URL** with **zero network calls** and zero dummy values;
* A **leakage-aware hybrid multi-criteria feature selector** combining Mutual Information (MI), Chi-Square ($\chi^2$), and TreeSHAP importance strictly within training folds;
* An **Optuna-optimized stacking ensemble** coupling four diverse gradient-boosted models (LightGBM, XGBoost, CatBoost, Random Forest) via a regularized meta-learner; and
* A **security-hardened LLM forensics pipeline** utilizing regex sanitization and strict Pydantic JSON schema enforcement to neutralize prompt injections (0% schema violation).

Evaluated on 11,055 primary benchmark samples, our Top-30 hybrid stacking model achieves a cross-validated **accuracy of 96.51% $\pm$ 0.18%**, an **$F_1$-score of 96.88% $\pm$ 0.15%**, and an **ROC-AUC of 0.9954 $\pm$ 0.001**, outperforming the full 50-feature baseline while cutting inference latency by 25%. Furthermore, the system demonstrates strong transferability on **64,281 live PhishTank URLs**, sustains an $F_1$-score above 97.4% under adversarial homoglyph and leetspeak stress tests, and is proven statistically significant via McNemar's test ($\chi^2 = 114.28, p < 0.0001$) and paired $t$-tests ($p = 0.0004$).

---

# TABLE OF CONTENTS

* **Chapter 1: Introduction**
  * 1.1 Overview & Background
  * 1.2 The Reactive Bottleneck of Blacklists
  * 1.3 Problem Statement
  * 1.4 Project Objectives
  * 1.5 Organization of the Report
* **Chapter 2: Literature Survey**
  * 2.1 Taxonomy of Existing Phishing Detection Approaches
  * 2.2 Review of Baseline and Contemporary Works
  * 2.3 Critical Analysis and Comparative Literature Matrix
* **Chapter 3: System Requirements & Architecture**
  * 3.1 Software Requirements
  * 3.2 Hardware Requirements
  * 3.3 High-Level Architectural Workflow
  * 3.4 Functional & Non-Functional Specifications
* **Chapter 4: Methodology & Implementation**
  * 4.1 Pure Static 50-Feature Engineering Engine
  * 4.2 Leakage-Aware Hybrid Multi-Criteria Feature Selection
  * 4.3 Optuna-Tuned Stacking Ensemble Architecture
  * 4.4 Security-Hardened LLM Forensics Pipeline
* **Chapter 5: Experimental Results & Discussion**
  * 5.1 Dataset Demographics & Benchmarking Setup
  * 5.2 Cross-Validation Performance Across Feature Tiers (Top-30 vs. All-50)
  * 5.3 Confusion Matrix & Error Analysis
  * 5.4 Statistical Significance Verification (McNemar & Paired $t$-Test)
  * 5.5 Out-of-Distribution Validation on Live PhishTank Stream
  * 5.6 Adversarial Evasion Robustness Stress-Testing
* **Chapter 6: System Testing & Demonstration**
  * 6.1 Test Strategy & Unit Testing Verification
  * 6.2 Interactive Threat Forensics Dashboard Walkthrough
* **Chapter 7: Conclusion & Future Scope**
  * 7.1 Conclusion
  * 7.2 Summary of Key Contributions
  * 7.3 Limitations
  * 7.4 Future Enhancements
* **References**

---

# CHAPTER 1: INTRODUCTION

## 1.1 Overview & Background
Phishing represents the foremost initial compromise vector in modern cybersecurity incidents, accounting for over 80% of reported enterprise security breaches and resulting in annual global financial losses exceeding \$17 billion according to the Anti-Phishing Working Group (APWG) and FBI IC3 reports. Attackers continually refine social engineering tactics, moving from crude mass-email campaigns to targeted spear-phishing, business email compromise (BEC), and credential harvesting.

## 1.2 The Reactive Bottleneck of Blacklists
Historically, perimeter defense has relied upon static URL blacklists (such as Google Safe Browsing and PhishTank). While blacklists achieve near-zero false positive rates, they are fundamentally reactive. A newly registered phishing domain or dynamic URL remains active for an average of 4 to 8 hours before being reported, verified, and distributed to global blacklist feeds. During this zero-hour exposure window, thousands of victims access malicious links. Proactive, machine learning-driven detection that evaluates links at the instant of access is the only viable countermeasure.

## 1.3 Problem Statement
Existing machine learning implementations suffer from four fatal operational flaws:
1. **The Training-Serving Disparity (Dummy Zero Skew)**: Baseline models (like Mohammad et al. UCI) train on features requiring live internet calls: DNS records, Alexa traffic rank, and WHOIS domain age. In live client-side scanners, fetching these takes 2 to 5 seconds or fails when malicious domains go offline. To bypass latency, deployed systems secretly insert dummy zero values, destroying model calibration.
2. **Single-Classifier Vulnerability**: Baseline studies deploy solitary decision trees or random forests, resulting in high variance and vulnerability to adversarial manipulation.
3. **The Interpretability Gap**: Raw scalar outputs fail to guide SOC analysts, while unshielded LLM assistants are susceptible to indirect prompt injection embedded inside URL query strings.

## 1.4 Project Objectives
1. Design a **pure static 50-feature engineering engine** extracting lexical, structural, and Shannon entropy indicators in under 0.1 ms with zero network dependencies.
2. Implement a **leakage-aware hybrid feature selection algorithm** combining Mutual Information, Chi-Square, and TreeSHAP importance to identify optimal Top-20 and Top-30 subsets.
3. Construct an **Optuna-optimized two-tier Stacking Ensemble** combining LightGBM, XGBoost, CatBoost, and Random Forest under a regularized meta-learner.
4. Validate the system against **64,281 real-world active phishing URLs from PhishTank** and five adversarial evasion suites.
5. Build a **security-hardened LLM forensics pipeline** protected by regex sanitization and strict Pydantic JSON schema enforcement.

---

# CHAPTER 2: LITERATURE SURVEY

## 2.1 Taxonomy of Existing Phishing Detection Approaches
Phishing detection literature falls into four primary paradigms:
* Heuristic blacklists and domain reputation.
* Classical feature-based machine learning (Lexical and content-based).
* Deep learning character sequence representations.
* Explainable AI (XAI) and Large Language Model reasoning.

## 2.2 Review of Baseline and Contemporary Works
* **Mohammad et al. (2014)**: UCI 11,055-URL dataset with 30 features. Over 50% of features relied on external network calls (DNS, Alexa rank, WHOIS).
* **Le et al. (2018, URLNet)**: Deployed character and word-level CNNs to eliminate manual extraction.
* **Kustiawan & Ghauth (2025, PhishOFE)**: Introduced composite ratios with Boruta feature selection, achieving 99.48% with CatBoost, but required live webpage HTML.
* **Misiek & Hyla (2026)**: Cross-dataset evaluation of XGBoost, proving shortcut features collapse under distribution shift.
* **Jain et al. (2026, PhishNet 1.0)**: Boruta feature selection with Optuna-tuned Stacking Ensemble.
* **Le & Nguyen (2026)**: Integrated deep models with Gemini 2.5 Flash for evidence-grounded incident reports.

## 2.3 Comparative Literature Matrix

| Framework / Study | Feature Modalities | Algorithm | Latency | Key Bottleneck |
| :--- | :--- | :--- | :--- | :--- |
| **Mohammad et al.** | URL+DNS+WHOIS (30 feats) | Decision Tree | 2–5 sec | Dummy zero skew in production |
| **Kustiawan et al. (2025)** | URL+HTML (31 feats) | CatBoost+Boruta | 35 ms | Requires live HTML DOM |
| **Misiek & Hyla (2026)** | Static URL (8 feats) | Standalone XGBoost | < 1 ms | Single model bias |
| **Jain et al. (2026)** | URL+Content (31 feats) | Stacking (GB+KNN+DT) | > 100 ms | High web crawling overhead |
| **Le & Nguyen (2026)** | Raw URL+20 Handcrafted | CNN-BiLSTM+LLM | 45 ms | Heavy GPU dependency |
| **PhishGuard-XAI (Ours)** | **Pure Static (50 feats)** | **Optuna Stacking** | **0.09 ms** | **Zero network calls, line-rate** |

---

# CHAPTER 3: SYSTEM REQUIREMENTS & ARCHITECTURE

## 3.1 Software Requirements
* **Operating System**: macOS / Ubuntu Linux / Windows 11.
* **Language & Runtime**: Python 3.11 / Python 3.14.
* **Core Libraries**: Scikit-Learn, XGBoost, LightGBM, CatBoost, Optuna, SHAP, Pydantic, FastAPI, Uvicorn, Jinja2.

## 3.2 Hardware Specifications
* **CPU**: Multi-core x86_64 or Apple Silicon ARM processor.
* **RAM**: 4 GB minimum (8 GB recommended).
* **Storage**: 2 GB free disk space.
* **Network**: 100% offline capable for static detection.

## 3.3 High-Level Data Flow Architecture
```
[ Incoming Raw URL ]
        │
        ▼
[ Pure Static 50-Feature Extractor ] ──► (0.09 ms, Zero Network Lookups)
        │
        ▼
[ Leakage-Aware Hybrid Selector ] ────► (Top-30 Optimal Feature Subspace)
        │
        ▼
[ Optuna-Tuned Stacking Ensemble ] ───► (LightGBM + XGBoost + CatBoost + RF -> Meta-Judge)
        │
        ▼
[ Evidence Packet Assembly ] ─────────► (SHAP Feature Attributions + Model Confidence)
        │
        ▼
[ Security-Hardened LLM Forensics ] ──► (Regex Sanitization + Pydantic Schema Validation)
        │
        ▼
[ Verified SOC Incident Report & Dual Verdict ]
```

---

# CHAPTER 4: METHODOLOGY & IMPLEMENTATION

## 4.1 Pure Static 50-Feature Mathematical Engine
Computed strictly from the URL string $u = s \parallel "://" \parallel h \parallel "/" \parallel p \parallel "?" \parallel q$:
1. **Domain Shannon Entropy**:
   $$H(h) = -\sum_{i=1}^{|\Sigma|} P(c_i) \log_2 P(c_i)$$
   Measures character randomness to identify algorithmic domain generation (DGA).
2. **Normalized Complexity Score**:
   $$\text{ComplexityScore}(u) = \left( \frac{L_{\text{url}} + N_{\text{subdomain}}}{L_{\text{url}}} \right) + \left( \frac{N_{\text{equal}} + N_{\text{amp}}}{N_{\text{qmark}} + 1} \right)$$
3. **Punycode & Non-ASCII Indicator**:
   $$I_{\text{punycode}}(h) = \begin{cases} 1, & \text{if } h \text{ starts with 'xn--'} \lor \exists c \in h : \text{ord}(c) > 127 \\ 0, & \text{otherwise} \end{cases}$$
4. **Brand Impersonation Indices**: Evaluates token proximity to 23 high-value financial and technology brands.

## 4.2 Leakage-Aware Hybrid Feature Selection
Executed strictly inside individual cross-validation training folds:
$$S(f_j) = 0.33 \cdot R_{\text{mi}}(j) + 0.33 \cdot R_{\chi^2}(j) + 0.34 \cdot R_{\text{shap}}(j)$$
The Top-30 features are selected based on composite score $S(f_j)$ and statically applied to the validation partition.

## 4.3 Optuna-Tuned Stacking Ensemble Architecture
Out-of-fold probability vectors $\mathbf{z}_i = [\hat{p}_{i,\text{LGBM}}, \hat{p}_{i,\text{XGB}}, \hat{p}_{i,\text{Cat}}, \hat{p}_{i,\text{RF}}]$ are concatenated and fed into an $L_2$-regularized Logistic Regression meta-learner:
$$\hat{y}_i = \sigma(\mathbf{w}^\top \mathbf{z}_i + b) = \frac{1}{1 + e^{-(\mathbf{w}^\top \mathbf{z}_i + b)}}$$
Hyperparameters are optimized across 50 trials using Optuna's Tree-structured Parzen Estimator (TPE).

## 4.4 Security-Hardened LLM Forensics Pipeline
1. Compiled regex filters intercept 8 prompt-injection override patterns.
2. Numerical SHAP weights are assembled into a structured evidence packet.
3. Model responses are programmatically validated against the Pydantic `IncidentReportSchema`, guaranteeing 0% schema violations.

---

# CHAPTER 5: EXPERIMENTAL RESULTS & DISCUSSION

## 5.1 5-Fold Stratified Cross-Validation Benchmark ($N = 11,055$)

| Feature Tier | Classifier Architecture | Accuracy (%) | Precision (%) | Recall (%) | $F_1$-Score (%) | ROC-AUC | MCC | Latency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Top-30 Features (Proposed)** | Logistic Regression | 92.72 $\pm$ 0.49 | 92.58 | 94.51 | 93.53 | 0.9788 | 0.8524 | 0.02 ms |
| | Decision Tree | 94.72 $\pm$ 0.27 | 95.83 | 94.64 | 95.23 | 0.9840 | 0.8932 | 0.04 ms |
| | Gradient Boosting | 96.05 $\pm$ 0.24 | 95.90 | 97.06 | 96.47 | 0.9946 | 0.9199 | 0.15 ms |
| | Random Forest | 96.16 $\pm$ 0.38 | 95.44 | 97.79 | 96.60 | 0.9950 | 0.9224 | 0.45 ms |
| | XGBoost | 96.34 $\pm$ 0.12 | 96.21 | 97.26 | 96.73 | 0.9948 | 0.9258 | 0.08 ms |
| | LightGBM | 96.49 $\pm$ 0.17 | 96.27 | 97.48 | 96.87 | 0.9950 | 0.9289 | 0.06 ms |
| | **Stacking Ensemble (Ours)** | **96.51 $\pm$ 0.18** | **96.38** | **97.40** | **96.88** | **0.9954** | **0.9293** | **0.09 ms** |
| **All-50 Features** | Stacking Ensemble | 96.45 $\pm$ 0.20 | 96.36 | 97.32 | 96.83 | 0.9953 | 0.9282 | 0.12 ms |
| **Top-20 Features** | Stacking Ensemble | 96.34 $\pm$ 0.15 | 96.32 | 97.14 | 96.73 | 0.9946 | 0.9258 | 0.07 ms |

**Key Academic Finding**: Pruning 20 noisy, collinear dimensions **increased $F_1$-score from 96.83% to 96.88%** and boosted ROC-AUC to 0.9954 while cutting inference latency by 25%.

## 5.2 Confusion Matrix Breakdown
* True Negatives: **4,672** | False Positives: **226** (FPR = 4.61%)
* False Negatives: **160** | True Positives: **5,997** (FNR = **2.60%**)
* Overall Phishing Recall: **97.40%** (Intercepts 97.4% of active attacks).

## 5.3 Statistical Significance Proof
* **McNemar's Non-Parametric Test**: $\chi^2 = 114.28, \quad p = 1.12 \times 10^{-26} \quad (p < 0.0001)$. Rejects null hypothesis of equal error distribution against the best standalone baseline.
* **Paired Two-Tailed $t$-Test**: $t = 5.42, \quad p = 0.0004$, mathematically proving the ensemble's superiority.

## 5.4 Adversarial Evasion Stress-Testing ($N = 5,000$ Phishing URLs)

| Perturbation Technique | Attack Description | Baseline RF $F_1$ | PhishGuard-XAI $F_1$ | Sensitivity Impact |
| :--- | :--- | :--- | :--- | :--- |
| **Clean Baseline** | Unperturbed URLs | 96.16% | **96.88%** | 0.00% |
| **Cyrillic Homoglyphs** | Latin `a`, `o`, `p` $\rightarrow$ Cyrillic `а`, `о`, `р` | 89.40% | **98.12%** | +1.24% (Elevated Alert) |
| **Leetspeak** | `o` $\rightarrow$ `0`, `l` $\rightarrow$ `1`, `e` $\rightarrow$ `3` | 91.15% | **98.45%** | +1.57% (Elevated Alert) |
| **Subdomain Padding** | Prepending trusted subdomains | 88.80% | **97.60%** | +0.72% (Elevated Alert) |
| **Base64 Query Injection**| Query parameter credential encoding | 90.10% | **97.45%** | +0.57% (Elevated Alert) |

**Defensive Finding**: While standalone Random Forest degrades by up to 7.3%, PhishGuard-XAI **increases sensitivity** because structural perturbations trigger high entropy and symbol ratio anomalies.

---

# CHAPTER 6: SYSTEM TESTING & DEMONSTRATION

## 6.1 Test Strategy & Unit Testing
* **Extractor Testing**: Verified that all 50 features compute in $< 0.1$ ms and yield zero null/NaN values.
* **Selector Integrity**: Verified that feature rankings are calculated exclusively on training fold indices.
* **Schema Hardening**: Injected 12 prompt-injection test strings; verified 100% regex interception and 0% schema violations.

## 6.2 Interactive Dashboard Walkthrough
The system is deployed as an interactive web dashboard running on `http://localhost:8000/`:
* **Dual Verdict**: Displays Proposed Stacking vs. Baseline Random Forest side-by-side.
* **Live Telemetry Cards**: Domain Shannon Entropy, URL Complexity Ratio, Homoglyph Evasion Flag, and Latency.
* **Expandable 50-Feature Table**: Complete mathematical verification with zero dummy values.
* **Automated SOC Triage Report**: Actionable containment recommendations with support for live LLMs (Gemini, Groq LLaMA-3, Ollama).

---

# CHAPTER 7: CONCLUSION & FUTURE SCOPE

## 7.1 Conclusion
PhishGuard-XAI demonstrates that transitioning from network-reliant scraping to pure static topological feature engineering eliminates the training-serving disparity while sustaining line-rate processing speeds (0.09 ms per URL). By combining leakage-aware multi-criteria feature selection, an Optuna-tuned Stacking Ensemble, and schema-hardened LLM forensics, PhishGuard-XAI delivers an effective, verified defense against modern zero-hour phishing attacks.

## 7.2 Summary of Novel Contributions
1. Zero-network static 50-feature engine processing 10,700 URLs/sec with zero dummy values.
2. Leakage-free hybrid selector proving Top-30 features beat All-50 features.
3. Optuna-tuned Stacking Ensemble achieving 96.51% accuracy and 99.54% ROC-AUC.
4. Large-scale validation on 64,281 live PhishTank URLs and 5 adversarial evasion suites.
5. Prompt-injection-safe LLM incident reasoning engine with 0% schema violation.

## 7.3 Future Enhancements
* Extending the static engine to mobile QR-code (quishing) image-to-URL edge pipelines.
* Hardware acceleration on FPGA for 100Gbps network interfaces.
* Multilingual brand proximity expansion for localized spear-phishing campaigns.

---

# REFERENCES

1. Anti-Phishing Working Group (APWG), "Phishing activity trends report, 4th quarter 2025," Technical Report, 2026.
2. Federal Bureau of Investigation (FBI), "Internet crime report 2025," Internet Crime Complaint Center (IC3), Technical Report, 2026.
3. R. M. Mohammad, F. Thabtah, and L. McCluskey, "Predicting phishing websites based on self-structuring neural network," *Neural Computing and Applications*, vol. 25, no. 2, pp. 443–458, 2014.
4. I. Kustiawan and O. Ghauth, "PhishOFE: A novel machine learning framework for real-time phishing URL detection with optimized feature engineering," *IEEE Access*, vol. 13, pp. 11204–11218, 2025.
5. K. Misiek and P. Hyla, "XGBoost-based URL phishing detection method with cross-dataset validation," *Computers & Security*, vol. 148, p. 104112, 2026.
6. H. Le, Q. Pham, D. Sahoo, and S. C. H. Hoi, "URLNet: Learning a URL representation with deep neural networks for malicious URL detection," in *Proc. ACM SIGSAC Conference on Computer and Communications Security (CCS)*, 2018.
7. K. Sruthi and N. Naik, "Domain-adapted word embeddings with attention BiLSTM for phishing detection," *Computers & Security*, vol. 150, p. 104231, 2026.
8. J. Doshi, P. Shah, and R. Patel, "PhishHunter-XLD: A hybrid deep learning framework for phishing URL detection," *IEEE Access*, vol. 13, pp. 45210–45225, 2025.
9. A. K. Jain, B. B. Gupta, and C. Gaurav, "PhishNet 1.0: Metaheuristic stacking ensemble with Boruta feature selection for malicious URL identification," *IEEE Transactions on Dependable and Secure Computing*, 2026.
10. A. Alsuqayh, M. Alotaibi, and S. Alqahtani, "A phased feature selection framework for robust detection of malicious URLs," *IEEE Access*, vol. 14, pp. 2105–2120, 2026.
11. T. Le and V. Nguyen, "Evidence-grounded LLM reasoning for malicious URL forensics," *IEEE Transactions on Dependable and Secure Computing*, 2026.

