import ipaddress
import math
import re
from urllib.parse import urlparse


MAX_URL_LENGTH = 2048
ALLOWED_SCHEMES = {"http", "https"}
SPECIAL_CHARACTERS = re.compile(r"[^A-Za-z0-9]")


def _is_private_hostname(hostname: str) -> bool:
    try:
        address = ipaddress.ip_address(hostname.strip("[]"))
    except ValueError:
        return False
    return (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_reserved
        or address.is_multicast
        or address.is_unspecified
    )


def validate_url(url: str) -> str:
    """Validate a URL before feature extraction or any future network access."""
    candidate = url.strip()
    if not candidate:
        raise ValueError("URL cannot be empty")
    if len(candidate) > MAX_URL_LENGTH:
        raise ValueError(f"URL must be {MAX_URL_LENGTH} characters or fewer")

    parsed = urlparse(candidate)
    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise ValueError("Only http:// and https:// URLs are supported")
    if parsed.username or parsed.password:
        raise ValueError("URLs containing embedded usernames or passwords are not accepted")
    if not parsed.hostname:
        raise ValueError("URL must include a hostname")
    if _is_private_hostname(parsed.hostname):
        raise ValueError("Private, loopback, and local IP addresses are not accepted")
    try:
        parsed.port
    except ValueError as error:
        raise ValueError("URL contains an invalid port") from error
    return candidate


def _entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = {character: value.count(character) for character in set(value)}
    length = len(value)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


def extract_lexical_metadata(url: str) -> dict:
    """Return richer lexical signals for reporting and future retraining."""
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    path = parsed.path or ""
    query = parsed.query or ""
    fragment = parsed.fragment or ""
    letters = sum(character.isalpha() for character in url)
    digits = sum(character.isdigit() for character in url)
    special_characters = len(SPECIAL_CHARACTERS.findall(url))
    length = max(len(url), 1)
    labels = [label for label in hostname.split(".") if label]
    return {
        "URL_Length": len(url),
        "Domain_Length": len(hostname),
        "Path_Length": len(path),
        "Query_Length": len(query),
        "Fragment_Length": len(fragment),
        "Num_Dots": url.count("."),
        "Num_Hyphens": url.count("-"),
        "Num_Underscores": url.count("_"),
        "Num_Slashes": url.count("/"),
        "Num_Backslashes": url.count("\\"),
        "Num_Digits": digits,
        "Num_Letters": letters,
        "Num_Special_Characters": special_characters,
        "Digit_Ratio": round(digits / length, 6),
        "Letter_Ratio": round(letters / length, 6),
        "Special_Character_Ratio": round(special_characters / length, 6),
        "URL_Entropy": round(_entropy(url), 6),
        "Has_IP_Address": bool(_is_private_hostname(hostname) or _is_ip_address(hostname)),
        "Has_At_Symbol": "@" in url,
        "Has_Double_Slash": "//" in parsed.path,
        "Uses_HTTPS": parsed.scheme.lower() == "https",
        "Subdomain_Count": max(len(labels) - 2, 0),
        "Domain_Depth": len(labels),
        "Prefix_Suffix": "-" in hostname,
    }


def _is_ip_address(hostname: str) -> bool:
    try:
        ipaddress.ip_address(hostname.strip("[]"))
        return True
    except ValueError:
        return False