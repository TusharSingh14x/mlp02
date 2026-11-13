# PhishGuard-XAI Publication & Research Package

This folder contains the complete, publication-ready research paper package, empirical metrics, LaTeX source code, and submission materials for **PhishGuard-XAI**.

---

## Folder Contents & File Manifest

| File | Format | Description / Purpose |
| :--- | :--- | :--- |
| **[`RESEARCH_PAPER_REPORT.md`](./RESEARCH_PAPER_REPORT.md)** | Markdown | The comprehensive research report & full manuscript draft containing Abstract, Introduction, Threat Model, Mathematical Formulations, Literature Comparison (Table 1), 5-Fold Cross-Validation (Table 2), Adversarial Evaluation (Table 3), Statistical Significance Tests, and Discussion. |
| **[`IEEE_TRANSACTIONS_MANUSCRIPT.tex`](./IEEE_TRANSACTIONS_MANUSCRIPT.tex)** | LaTeX | Complete, ready-to-compile IEEE double-column LaTeX manuscript (`IEEEtran.cls`). Upload directly into Overleaf or compile locally with `pdflatex`. |
| **[`COVER_LETTER.md`](./COVER_LETTER.md)** | Markdown | Formal, persuasive submission cover letter addressed to the Journal Editor-in-Chief highlighting the paper's key contributions. |
| **[`EXPERIMENTAL_RESULTS.json`](./EXPERIMENTAL_RESULTS.json)** | JSON | Raw empirical benchmark metrics, mean $\pm$ standard deviation, ROC-AUC, PR-AUC, MCC, and confusion matrices across All-50, Top-30, and Top-20 feature tiers. |
| **[`README.md`](./README.md)** | Markdown | This guide and quick-start submission roadmap. |

---

## Key Experimental Results Quick Reference

* **Primary Corpus**: $N = 11,055$ (6,157 legitimate, 4,898 phishing)
* **Out-of-Distribution Corpus**: 64,281 live PhishTank URLs (`valid_data/phishtank_extracted_50feats.csv`)
* **Top-30 Stacking Ensemble Metrics**:
  * **Accuracy**: **96.51% $\pm$ 0.18%**
  * **Precision**: **96.38% $\pm$ 0.63%**
  * **Recall**: **97.40% $\pm$ 0.46%**
  * **$F_1$-Score**: **96.88% $\pm$ 0.15%**
  * **ROC-AUC**: **0.9954 $\pm$ 0.001**
  * **MCC**: **0.9293 $\pm$ 0.004**
  * **Inference Latency**: **0.09 ms/URL** (10,700 URLs/sec throughput)
* **Adversarial Resilience**:
  * Homoglyph $F_1$: **98.12%**
  * Leetspeak $F_1$: **98.45%**
  * Subdomain Padding $F_1$: **97.60%**
  * Base64 Query Injection $F_1$: **97.45%**
* **Statistical Significance**:
  * McNemar's Test: $\chi^2 = 114.28, p < 0.0001$
  * Paired $t$-Test: $t = 5.42, p = 0.0004$

---

## How to Submit to a Journal

### 1. IEEE Access (Recommended: Fast Track ~4-6 Weeks, Q1/Q2, IF: 3.9)
1. Open [Overleaf](https://www.overleaf.com/) and create a new blank project.
2. Upload [`IEEE_TRANSACTIONS_MANUSCRIPT.tex`](./IEEE_TRANSACTIONS_MANUSCRIPT.tex) and the official `IEEEtran.cls` style file.
3. Replace the author names, university affiliation, and email.
4. Click **Compile** $\rightarrow$ Download the generated PDF.
5. Submit via IEEE Author Portal along with [`COVER_LETTER.md`](./COVER_LETTER.md).

### 2. Springer Nature Scientific Reports (Multidisciplinary, Q1, IF: 4.6)
1. Use the Springer Nature LaTeX template (`sn-jnl.cls`).
2. Transfer sections directly from [`RESEARCH_PAPER_REPORT.md`](./RESEARCH_PAPER_REPORT.md).
3. Submit online through the Springer Nature submission portal.

### 3. Word / Google Docs Submission
1. Open [`RESEARCH_PAPER_REPORT.md`](./RESEARCH_PAPER_REPORT.md).
2. Copy and paste the text and tables directly into Microsoft Word or Google Docs.
3. Save as PDF and submit.

