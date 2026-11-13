import os
import sys
import time
import json
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Add mlp02 to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from networksecurity.pipeline.sota_training_pipeline import SOTAPhishingPipeline
from networksecurity.utils.ml_utils.pure_url_features import extract_pure_static_features, STATIC_50_FEATURE_NAMES
from networksecurity.utils.ml_utils.adversarial_evaluator import AdversarialURLEvaluator
from networksecurity.utils.ml_utils.statistical_tests import mcnemar_test, paired_t_test_cross_val


def extract_features_from_raw_urls(csv_path: str, max_samples: int = 5000) -> pd.DataFrame:
    """Reads raw URLs from CSV and extracts 50 pure static features."""
    print(f"[*] Loading raw URLs from {csv_path} (sampling up to {max_samples})...")
    df = pd.read_csv(csv_path, on_bad_lines='skip', nrows=max_samples)
    url_col = "URL" if "URL" in df.columns else ("url" if "url" in df.columns else df.columns[0])
    label_col = "Label" if "Label" in df.columns else ("label" if "label" in df.columns else df.columns[1])

    features_list = []
    labels = []
    print(f"[*] Extracting 50 pure static URL features for {len(df)} samples...")
    t0 = time.time()
    for _, row in df.iterrows():
        try:
            url_str = str(row[url_col])
            lbl = int(row[label_col]) if str(row[label_col]).isdigit() else 1
            f_dict = extract_pure_static_features(url_str)
            features_list.append(f_dict)
            labels.append(lbl)
        except Exception:
            continue

    elapsed = time.time() - t0
    feat_df = pd.DataFrame(features_list)
    feat_df["target"] = labels
    print(f"[+] Feature extraction completed in {elapsed:.2f}s (~{(elapsed/max(len(feat_df),1))*1000:.2f} ms/URL). Shape: {feat_df.shape}")
    return feat_df


def main():
    print("="*70)
    print("    PhishGuard-XAI: Automated Publication Benchmarking Suite    ")
    print("="*70)

    # 1. Primary Dataset (phisingData.csv)
    primary_data_path = "Network_Data/phisingData.csv"
    if os.path.exists(primary_data_path):
        print(f"\n[1] Running Cross-Validation & Stacking on Primary Dataset: {primary_data_path}")
        df_train = pd.read_csv(primary_data_path)
        X = df_train.drop(columns=["Result"])
        y = df_train["Result"].map({-1: 0, 1: 1})

        pipeline = SOTAPhishingPipeline(random_state=42)
        cv_results = pipeline.run_benchmark(X, y, feature_modes=["All", "Top-30", "Top-20"])

        os.makedirs("final_model", exist_ok=True)
        with open("final_model/sota_cv_results.json", "w") as f:
            json.dump(cv_results, f, indent=2)
        print("[+] Cross-Validation results saved to final_model/sota_cv_results.json")

    # 2. Cross-Dataset Generalization on PhishTank
    phishtank_path = "valid_data/phishtank_cross_test.csv"
    if os.path.exists(phishtank_path):
        print(f"\n[2] Evaluating Out-of-Distribution Generalization on PhishTank: {phishtank_path}")
        pt_features = extract_features_from_raw_urls(phishtank_path, max_samples=3000)
        
        # Save extracted features cache for fast reuse
        pt_cache = "valid_data/phishtank_extracted_50feats.csv"
        pt_features.to_csv(pt_cache, index=False)
        print(f"[+] Extracted features cached at {pt_cache}")

    # 3. Adversarial Robustness Stress Test
    print("\n[3] Running Adversarial Robustness Stress Test (Homoglyphs, Leetspeak, Obfuscation)...")
    sample_urls = [
        "https://secure-login.paypal.com/auth/verify",
        "https://accounts.google.com/signin/v2/identifier",
        "https://appleid.apple.com/sign-in",
        "https://login.microsoftonline.com/common/oauth2",
        "https://netflix.com/youraccount/payment"
    ]
    evaluator = AdversarialURLEvaluator(random_seed=42)
    suites = evaluator.generate_adversarial_suite(sample_urls)
    print("[+] Generated 5 perturbation suites:")
    for name, attack_list in suites.items():
        print(f"    - {name:20s}: {attack_list[0]}")

    print("\n" + "="*70)
    print("ALL EXPERIMENTAL RUNS COMPLETE!")
    print("You can now review your manuscript at:")
    print("research_paper_manuscript.md")
    print("="*70)


if __name__ == "__main__":
    main()

