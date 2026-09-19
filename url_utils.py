"""
URL normalization helpers.

Amazon product links usually carry a title slug and tracking/referral query
params (?ref=sr_1_3&keywords=...) that are irrelevant to what the product
actually is. Left as-is, the same product pasted from two different places
(a search result vs. a share link) would be treated as two different
watchlist entries. normalize_amazon_url() strips all of that down to the
canonical https://<domain>/dp/<ASIN> form.
"""

import re
from urllib.parse import urlparse

ASIN_PATTERN = re.compile(r"/(?:dp|gp/product|product)/([A-Z0-9]{10})", re.IGNORECASE)


def normalize_amazon_url(url):
    """Canonicalize an Amazon product URL to https://<domain>/dp/<ASIN>.
    Falls back to the original URL unchanged if no ASIN can be found (e.g.
    a shortened amzn.in link), so it's always safe to call."""
    match = ASIN_PATTERN.search(url)
    if not match:
        return url

    asin = match.group(1).upper()
    domain = urlparse(url).netloc or "www.amazon.in"
    return f"https://{domain}/dp/{asin}"
