import ipaddress
import math
import re
from urllib.parse import urlparse
from typing import Dict, Any, List

import numpy as np
import pandas as pd

from networksecurity.utils.ml_utils.url_security import validate_url

SHORTENING_SERVICES = {
    "bit.ly", "goo.gl", "is.gd", "ow.ly", "t.co", "tinyurl.com",
    "buff.ly", "cutt.ly", "rebrand.ly", "shorturl.at", "tiny.cc",
    "clck.ru", "is.gd", "v.gd", "tr.im", "s.id"
}

SUSPICIOUS_TLDS = {
    "tk", "ml", "ga", "cf", "gq", "xyz", "top", "work", "club",
    "loan", "buzz", "guru", "surf", "casa", "fit", "rest", "bar",
    "monster", "stream", "live", "link", "click"
}

TARGETED_BRANDS = [
    "paypal", "apple", "google", "microsoft", "amazon", "netflix",
    "facebook", "instagram", "chase", "wellsfargo", "bankofamerica",
    "citibank", "whatsapp", "linkedin", "dropbox", "ebay", "binance",
    "coinbase", "metamask", "steam", "icloud", "outlook", "yahoo"
]

PHISHING_KEYWORDS = [
    "login", "verify", "update", "secure", "account", "banking",
    "confirm", "password", "payment", "webscr", "support", "security",
    "authentication", "signin", "wallet", "suspended", "recover"
]

STATIC_50_FEATURE_NAMES: List[str] = [
    # 1-21: Lexical features
    "url_length", "hostname_length", "path_length", "query_length",
    "num_digits", "digit_ratio", "num_hyphens", "num_dots", "num_slashes",
    "num_question_marks", "num_equals", "num_at_symbols", "num_percent",
    "num_ampersand", "num_underscore", "num_special_chars", "special_char_ratio",
    "has_ip", "is_https", "uppercase_ratio", "is_shortened",
    # 22-31: Host & Domain features
    "domain_length", "tld_length", "subdomain_count", "has_hyphen_in_domain",
    "has_digit_in_domain", "domain_entropy", "suspicious_tld_flag",
    "brand_impersonation_score", "is_punycode", "domain_token_count",
    # 32-37: Structural features
    "path_depth", "param_count", "has_double_slash_in_path",
    "path_entropy", "query_entropy", "has_fragment",
    # 38-43: Statistical & Information Theoretic
    "shannon_entropy", "char_diversity", "token_count",
    "avg_token_length", "max_token_length", "unique_token_ratio",
    # 44-46: Composite features
    "suspicious_char_ratio", "url_complexity_score", "entropy_to_length_ratio",
    # 47-50: Semantic/Keyword indicators
    "has_login_keyword", "has_verify_keyword", "has_account_keyword",
    "phishing_keyword_count"
]


def calculate_shannon_entropy(text: str) -> float:
    """Calculate the Shannon entropy of a given string."""
    if not text:
        return 0.0
    length = len(text)
    freqs = {}
    for char in text:
        freqs[char] = freqs.get(char, 0) + 1
    entropy = 0.0
    for count in freqs.values():
        p = count / length
        entropy -= p * math.log2(p)
    return round(entropy, 4)


def _check_ip_in_hostname(hostname: str) -> int:
    try:
        ipaddress.ip_address(hostname.strip("[]"))
        return 1
    except ValueError:
        # Check for hex/octal or dotted numeric patterns
        if re.search(r"^\d{1,3}(\.\d{1,3}){3}$", hostname):
            return 1
        return 0


def extract_pure_static_features(url: str) -> Dict[str, Any]:
    """
    Extract 50 pure static, client-side, zero-network URL features.
    Guarantees no dummy zeros or unpopulated attributes.
    """
    raw_url = url.strip()
    candidate = validate_url(raw_url if "://" in raw_url else f"https://{raw_url}")
    parsed = urlparse(candidate)
    hostname = (parsed.hostname or "").lower()
    path = parsed.path or ""
    query = parsed.query or ""
    fragment = parsed.fragment or ""

    url_len = len(candidate)
    host_len = len(hostname)
    path_len = len(path)
    query_len = len(query)

    # Character counts
    num_digits = sum(c.isdigit() for c in candidate)
    digit_ratio = num_digits / max(url_len, 1)
    num_hyphens = candidate.count("-")
    num_dots = candidate.count(".")
    num_slashes = candidate.count("/")
    num_qmark = candidate.count("?")
    num_equals = candidate.count("=")
    num_at = candidate.count("@")
    num_percent = candidate.count("%")
    num_amp = candidate.count("&")
    num_underscore = candidate.count("_")
    
    special_chars = set("!@#$%^&*()_+-=[]{}|;':\",./<>?`~")
    num_special = sum(c in special_chars for c in candidate)
    special_char_ratio = num_special / max(url_len, 1)

    has_ip = _check_ip_in_hostname(hostname)
    is_https = 1 if parsed.scheme.lower() == "https" else 0
    uppercase_ratio = sum(c.isupper() for c in raw_url) / max(len(raw_url), 1)
    is_shortened = 1 if hostname in SHORTENING_SERVICES else 0

    # Host & Domain decomposition
    host_labels = [p for p in hostname.split(".") if p]
    tld = host_labels[-1] if host_labels else ""
    tld_length = len(tld)
    subdomain_count = max(len(host_labels) - 2, 0)
    domain_length = host_len
    has_hyphen_in_domain = 1 if "-" in hostname else 0
    has_digit_in_domain = 1 if any(c.isdigit() for c in hostname) else 0
    domain_entropy = calculate_shannon_entropy(hostname)
    suspicious_tld_flag = 1 if tld in SUSPICIOUS_TLDS else 0

    brand_impersonation_score = sum(1 for brand in TARGETED_BRANDS if brand in hostname)
    is_punycode = 1 if "xn--" in hostname or any(ord(c) > 127 for c in raw_url) else 0
    domain_token_count = len(host_labels)

    # Structural
    path_segments = [s for s in path.split("/") if s]
    path_depth = len(path_segments)
    query_params = [q for q in query.split("&") if q]
    param_count = len(query_params)
    has_double_slash_in_path = 1 if "//" in path else 0
    path_entropy = calculate_shannon_entropy(path)
    query_entropy = calculate_shannon_entropy(query)
    has_fragment = 1 if len(fragment) > 0 else 0

    # Statistical & token metrics
    tokens = re.split(r"[^A-Za-z0-9]", candidate)
    tokens = [t for t in tokens if t]
    token_count = len(tokens)
    token_lengths = [len(t) for t in tokens] if tokens else [0]
    avg_token_length = float(np.mean(token_lengths))
    max_token_length = int(np.max(token_lengths))
    unique_token_ratio = len(set(tokens)) / max(token_count, 1)
    shannon_entropy = calculate_shannon_entropy(candidate)
    char_diversity = len(set(candidate)) / max(url_len, 1)

    # Composite metrics (PhishOFE & Duarte 2025/2026 formulations)
    suspicious_char_ratio = (num_special + num_equals + num_qmark + num_amp) / max(url_len, 1)
    first_term = (url_len + subdomain_count) / max(url_len, 1)
    second_term = (num_equals + num_amp) / (num_qmark + 1.0)
    url_complexity_score = round(first_term + second_term, 4)
    entropy_to_length_ratio = shannon_entropy / max(math.log2(url_len + 1), 1.0)

    # Semantic keyword metrics
    lower_url = candidate.lower()
    has_login_keyword = 1 if "login" in lower_url or "signin" in lower_url else 0
    has_verify_keyword = 1 if "verify" in lower_url or "confirm" in lower_url else 0
    has_account_keyword = 1 if "account" in lower_url or "banking" in lower_url else 0
    phishing_keyword_count = sum(1 for kw in PHISHING_KEYWORDS if kw in lower_url)

    features: Dict[str, Any] = {
        "url_length": url_len,
        "hostname_length": host_len,
        "path_length": path_len,
        "query_length": query_len,
        "num_digits": num_digits,
        "digit_ratio": round(digit_ratio, 4),
        "num_hyphens": num_hyphens,
        "num_dots": num_dots,
        "num_slashes": num_slashes,
        "num_question_marks": num_qmark,
        "num_equals": num_equals,
        "num_at_symbols": num_at,
        "num_percent": num_percent,
        "num_ampersand": num_amp,
        "num_underscore": num_underscore,
        "num_special_chars": num_special,
        "special_char_ratio": round(special_char_ratio, 4),
        "has_ip": has_ip,
        "is_https": is_https,
        "uppercase_ratio": round(uppercase_ratio, 4),
        "is_shortened": is_shortened,
        "domain_length": domain_length,
        "tld_length": tld_length,
        "subdomain_count": subdomain_count,
        "has_hyphen_in_domain": has_hyphen_in_domain,
        "has_digit_in_domain": has_digit_in_domain,
        "domain_entropy": domain_entropy,
        "suspicious_tld_flag": suspicious_tld_flag,
        "brand_impersonation_score": brand_impersonation_score,
        "is_punycode": is_punycode,
        "domain_token_count": domain_token_count,
        "path_depth": path_depth,
        "param_count": param_count,
        "has_double_slash_in_path": has_double_slash_in_path,
        "path_entropy": path_entropy,
        "query_entropy": query_entropy,
        "has_fragment": has_fragment,
        "shannon_entropy": shannon_entropy,
        "char_diversity": round(char_diversity, 4),
        "token_count": token_count,
        "avg_token_length": round(avg_token_length, 4),
        "max_token_length": max_token_length,
        "unique_token_ratio": round(unique_token_ratio, 4),
        "suspicious_char_ratio": round(suspicious_char_ratio, 4),
        "url_complexity_score": round(url_complexity_score, 4),
        "entropy_to_length_ratio": round(entropy_to_length_ratio, 4),
        "has_login_keyword": has_login_keyword,
        "has_verify_keyword": has_verify_keyword,
        "has_account_keyword": has_account_keyword,
        "phishing_keyword_count": phishing_keyword_count,
    }
    return features


def extract_pure_static_dataframe(url: str) -> pd.DataFrame:
    """Return static features formatted as a single-row DataFrame."""
    feature_dict = extract_pure_static_features(url)
    return pd.DataFrame([[feature_dict[col] for col in STATIC_50_FEATURE_NAMES]], columns=STATIC_50_FEATURE_NAMES)

