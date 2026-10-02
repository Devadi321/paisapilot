"""Best-effort price extraction for the Deal Watch feature.

Tries, in order:
1. JSON-LD / meta tags (og:price:amount, product:price:amount)
2. Common price patterns near ₹ / Rs. / $ symbols

Returns (price: float | None, error: str | None). Never raises.
"""
import re
import urllib.request

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) PaisaPilot/0.1 (price check)"}

PRICE_PATTERNS = [
    r'"price"\s*:\s*"([\d,]+\.?\d*)"',
    r'property="og:price:amount"\s+content="([\d,\.]+)"',
    r'property="product:price:amount"\s+content="([\d,\.]+)"',
    r'₹\s*([\d,]+(?:\.\d{1,2})?)',
    r'Rs\.?\s*([\d,]+(?:\.\d{1,2})?)',
    r'\$\s*([\d,]+(?:\.\d{1,2})?)',
]


def check_price(url):
    if not url:
        return None, "no URL provided"
    if not url.startswith(("http://", "https://")):
        return None, "URL must start with http(s)://"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:  # noqa: BLE001
        return None, f"could not fetch page ({type(e).__name__})"
    for pat in PRICE_PATTERNS:
        m = re.search(pat, html)
        if m:
            try:
                return float(m.group(1).replace(",", "")), None
            except ValueError:
                continue
    return None, "no price found on page"
