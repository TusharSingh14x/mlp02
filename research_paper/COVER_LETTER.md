# Formal Cover Letter for Journal Submission

**To:**  
Editor-in-Chief,  
*IEEE Access* / *Scientific Reports* / *Computers & Security*

**Date:** November 13, 2026  
**Subject:** Submission of Original Research Manuscript: *"PhishGuard-XAI: A Security-Hardened, Phased Feature Selection and Metaheuristic Stacking Framework for Robust Phishing URL Detection"*

Dear Editor-in-Chief,

We are pleased to submit our original research manuscript entitled **"PhishGuard-XAI: A Security-Hardened, Phased Feature Selection and Metaheuristic Stacking Framework for Robust Phishing URL Detection"** for consideration as a regular research article in your prestigious journal.

### Summary and Core Motivation
Phishing attacks remain the leading threat vector in modern cyber warfare, accounting for over 80% of reported enterprise security incidents. While contemporary machine learning literature reports theoretical accuracies exceeding 98%, existing production implementations suffer from four critical systemic vulnerabilities:
1. **Training-Serving Feature Disparity**: Baseline models trained on live WHOIS, DOM tags, and DNS lookups must insert unpopulated dummy zero values during real-time edge scanning, severely degrading detection accuracy.
2. **Cross-Dataset Generalization Collapse**: Models overfit static benchmark distributions, suffering sharp recall degradation when exposed to unseen live feeds.
3. **The Interpretability-Actionability Gap**: Raw numerical feature attributions fail to provide actionable, contextualized triage guidance to Security Operations Center (SOC) analysts.
4. **Vulnerability to Adversarial Evasions & Prompt Injections**: Attackers increasingly utilize Unicode Cyrillic homoglyphs, leetspeak, or embed adversarial instructions directly into URL query parameters to hijack LLM-assisted pipelines.

### Key Contributions & Novel Findings
Our manuscript addresses these coupled challenges through five significant contributions:
* **Zero-Network Static 50-Feature Engineering Engine**: Extracts lexical, structural, and Shannon entropy indicators in **under 0.09 ms per URL** with zero network roundtrips and zero dummy values, achieving a line-rate gateway throughput of **10,700 URLs/second**.
* **Leakage-Aware Hybrid Multi-Criteria Feature Selection**: Unifies Mutual Information (MI), Chi-Square ($\chi^2$), and TreeSHAP importance strictly within cross-validation folds. We empirically demonstrate that our **Top-30 feature tier outperforms the full 50-feature space**, proving that pruning collinear dimensions eliminates boundary overfitting.
* **Optuna-Tuned Stacking Ensemble**: Couples LightGBM, XGBoost, CatBoost, and Random Forest under an $L_2$-regularized meta-learner, achieving **96.51% accuracy**, **96.88% $F_1$-score**, and **99.54% ROC-AUC** across 5-fold cross-validation.
* **Large-Scale Out-of-Distribution & Adversarial Stress Testing**: Evaluates transferability against **64,281 live PhishTank URLs** and five synthetic evasion classes (Cyrillic homoglyphs, leetspeak, Base64 parameter injection), sustaining an $F_1$-score exceeding 97.4%.
* **Security-Hardened, Schema-Grounded LLM Reasoning Engine**: Enforces regex sanitization and strict Pydantic JSON schema validation, neutralizing prompt injections (**0% schema violation**) while generating human-interpretable SOC triage reports.

### Statements of Originality and Compliance
* This manuscript represents original work that has not been published previously, is not currently under consideration for publication elsewhere, and will not be submitted elsewhere while under review in your journal.
* All experimental data, benchmark scripts, and source implementations have been documented for reproducibility.
* There are no conflicts of interest to declare.

We believe that our focus on eliminating the training-serving disparity, achieving line-rate edge processing, and securing LLM-assisted incident triage aligns directly with the scope of your journal and will be of substantial interest to cybersecurity researchers, network engineers, and machine learning practitioners.

Thank you very much for your time and consideration.

Sincerely,

**Tushar Singh, Eshan, and Rudra**  
Department of Computer Science and Engineering  
Indian Institute of Information Technology, Nagpur (IIITN)  
Nagpur, Maharashtra, India  
Email: tushar@iiitn.ac.in

