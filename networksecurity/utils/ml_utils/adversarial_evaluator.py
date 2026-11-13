import re
import random
import base64
from urllib.parse import urlparse, urlunparse
from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


# Common homoglyph mappings (Latin -> Cyrillic/Greek lookalikes)
HOMOGLYPH_MAP = {
    'a': 'а',  # Cyrillic small letter a
    'c': 'с',  # Cyrillic small letter es
    'e': 'е',  # Cyrillic small letter ie
    'i': 'і',  # Cyrillic small letter byelorussian-ukrainian i
    'j': 'ј',  # Cyrillic small letter je
    'o': 'о',  # Cyrillic small letter o
    'p': 'р',  # Cyrillic small letter er
    's': 'ѕ',  # Cyrillic small letter dze
    'x': 'х',  # Cyrillic small letter ha
    'y': 'у',  # Cyrillic small letter u
}

LEETSPEAK_MAP = {
    'o': '0',
    'l': '1',
    'i': '1',
    'e': '3',
    'a': '4',
    's': '5',
    't': '7',
    'b': '8',
}


class AdversarialURLEvaluator:
    """
    Evaluates phishing detector robustness against real-world adversarial evasion tactics:
      1. Homoglyph Substitution (IDN / Punycode visual spoofing)
      2. Leetspeak obfuscation
      3. Excessive Subdomain Chaining / Padding
      4. Hex / URL Percent-Encoding
      5. Base64-encoded Parameter Injection
    """

    def __init__(self, random_seed: int = 42):
        self.random_state = random.Random(random_seed)

    def apply_homoglyph(self, url: str) -> str:
        """Replace 1-2 Latin characters with visually identical Cyrillic characters."""
        parsed = urlparse(url)
        host = parsed.netloc
        chars = list(host)
        candidates = [i for i, c in enumerate(chars) if c.lower() in HOMOGLYPH_MAP]
        if candidates:
            idx = self.random_state.choice(candidates)
            chars[idx] = HOMOGLYPH_MAP[chars[idx].lower()]
        new_host = "".join(chars)
        return urlunparse(parsed._replace(netloc=new_host))

    def apply_leetspeak(self, url: str) -> str:
        """Substitute characters with numbers (e.g., google -> g00gle)."""
        chars = list(url)
        candidates = [i for i, c in enumerate(chars) if c.lower() in LEETSPEAK_MAP]
        if candidates:
            # Substitute up to 2 characters
            for idx in self.random_state.sample(candidates, min(2, len(candidates))):
                chars[idx] = LEETSPEAK_MAP[chars[idx].lower()]
        return "".join(chars)

    def apply_subdomain_padding(self, url: str) -> str:
        """Append deceptive trusted subdomains (e.g. paypal.com.verify.attacker.net)."""
        parsed = urlparse(url)
        host = parsed.netloc
        prefixes = ["login-verify-account", "secure-banking-portal", "auth-session-update", "id-support-service"]
        chosen = self.random_state.choice(prefixes)
        new_host = f"{chosen}.{host}"
        return urlunparse(parsed._replace(netloc=new_host))

    def apply_percent_encoding(self, url: str) -> str:
        """Percent-encode delimiters to evade naive regex parsers."""
        return url.replace("/", "%2F").replace("?", "%3F").replace("=", "%3D")

    def apply_base64_payload(self, url: str) -> str:
        """Inject Base64 encoded payload into query parameters."""
        payload = base64.b64encode(b"session_token_login_auth_credentials").decode("utf-8")
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}auth_redirect={payload}"

    def generate_adversarial_suite(self, urls: List[str]) -> Dict[str, List[str]]:
        """Generate test suites for each perturbation category."""
        return {
            "Original": urls,
            "Homoglyph": [self.apply_homoglyph(u) for u in urls],
            "Leetspeak": [self.apply_leetspeak(u) for u in urls],
            "Subdomain_Padding": [self.apply_subdomain_padding(u) for u in urls],
            "Base64_Payload": [self.apply_base64_payload(u) for u in urls],
        }

    def evaluate_model_robustness(
        self, model: Any, feature_extractor_fn, urls: List[str], ground_truth: List[int]
    ) -> pd.DataFrame:
        """Run all attack vectors and measure degradation in Accuracy, Recall, and F1."""
        suites = self.generate_adversarial_suite(urls)
        results = []

        for attack_name, attack_urls in suites.items():
            # Extract features for each perturbed URL
            features_list = [feature_extractor_fn(u) for u in attack_urls]
            X = pd.concat(features_list, ignore_index=True)
            y_pred = model.predict(X)

            acc = accuracy_score(ground_truth, y_pred)
            prec = precision_score(ground_truth, y_pred, zero_division=0)
            rec = recall_score(ground_truth, y_pred, zero_division=0)
            f1 = f1_score(ground_truth, y_pred, zero_division=0)

            results.append({
                "Perturbation": attack_name,
                "Accuracy": round(acc, 4),
                "Precision": round(prec, 4),
                "Recall": round(rec, 4),
                "F1_Score": round(f1, 4),
                "F1_Degradation": round(results[0]["F1_Score"] - f1 if results else 0.0, 4)
            })

        return pd.DataFrame(results)

