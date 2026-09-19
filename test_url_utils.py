from url_utils import normalize_amazon_url


def test_normalizes_dp_url_with_title_slug_and_tracking_params():
    url = (
        "https://www.amazon.in/Sony-WH-1000XM4-Cancelling-Headphones/dp/B0863TXGM3"
        "/ref=sr_1_3?crid=ABC123&keywords=headphones&qid=1234567890&sr=8-3"
    )
    assert normalize_amazon_url(url) == "https://www.amazon.in/dp/B0863TXGM3"


def test_normalizes_gp_product_url():
    url = "https://www.amazon.in/gp/product/B0863TXGM3/ref=ox_sc_act_title_1"
    assert normalize_amazon_url(url) == "https://www.amazon.in/dp/B0863TXGM3"


def test_already_canonical_url_is_unchanged():
    url = "https://www.amazon.in/dp/B0863TXGM3"
    assert normalize_amazon_url(url) == url


def test_preserves_different_amazon_domain():
    url = "https://www.amazon.com/dp/B0863TXGM3?tag=affiliate-20"
    assert normalize_amazon_url(url) == "https://www.amazon.com/dp/B0863TXGM3"


def test_asin_is_uppercased():
    url = "https://www.amazon.in/dp/b0863txgm3"
    assert normalize_amazon_url(url) == "https://www.amazon.in/dp/B0863TXGM3"


def test_falls_back_to_original_url_when_no_asin_found():
    url = "https://amzn.in/d/abc123"
    assert normalize_amazon_url(url) == url
