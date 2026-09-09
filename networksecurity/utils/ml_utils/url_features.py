import ipaddress
from urllib.parse import urlparse

import pandas as pd

from networksecurity.constant.training_pipeline import FEATURE_COLUMNS
from networksecurity.utils.ml_utils.url_security import validate_url


SHORTENING_SERVICES = {
    "bit.ly",
    "goo.gl",
    "is.gd",
    "ow.ly",
    "t.co",
    "tinyurl.com",
    "buff.ly",
    "cutt.ly",
    "rebrand.ly",
}


def _has_ip_address(hostname: str) -> bool:
    try:
        ipaddress.ip_address(hostname.strip("[]"))
        return True
    except ValueError:
        return False


def extract_url_features(url: str) -> pd.DataFrame:
    """Convert a URL into the feature representation used by the dataset."""
    candidate = validate_url(url if "://" in url else f"https://{url}")
    parsed = urlparse(candidate)
    hostname = (parsed.hostname or "").lower()
    if not hostname:
        raise ValueError("Enter a valid URL with a hostname")

    labels = [part for part in hostname.split(".") if part]
    extra_slash = "//" in parsed.path
    port = parsed.port
    nonstandard_port = port is not None and port not in {80, 443}

    values = {
        "having_IP_Address": -1 if _has_ip_address(hostname) else 1,
        "URL_Length": -1 if len(candidate) > 75 else (0 if len(candidate) > 54 else 1),
        "Shortining_Service": -1 if hostname in SHORTENING_SERVICES else 1,
        "having_At_Symbol": -1 if "@" in candidate else 1,
        "double_slash_redirecting": -1 if extra_slash else 1,
        "Prefix_Suffix": -1 if "-" in hostname else 1,
        "having_Sub_Domain": -1 if len(labels) > 3 else (0 if len(labels) == 3 else 1),
        "SSLfinal_State": 1 if parsed.scheme.lower() == "https" else -1,
        "Domain_registeration_length": 0,
        "Favicon": 0,
        "port": -1 if nonstandard_port else 1,
        "HTTPS_token": -1 if "https" in hostname else 1,
        "Request_URL": 0,
        "URL_of_Anchor": 0,
        "Links_in_tags": 0,
        "SFH": 0,
        "Submitting_to_email": -1 if "mailto:" in candidate.lower() else 1,
        "Abnormal_URL": -1 if parsed.netloc != hostname else 1,
        "Redirect": -1 if len(parsed.path.split("/")[:-1]) > 3 else 1,
        "on_mouseover": 0,
        "RightClick": 0,
        "popUpWidnow": 0,
        "Iframe": 0,
        "age_of_domain": 0,
        "DNSRecord": 0,
        "web_traffic": 0,
        "Page_Rank": 0,
        "Google_Index": 0,
        "Links_pointing_to_page": 0,
        "Statistical_report": 1,
    }
    return pd.DataFrame([[values[column] for column in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)