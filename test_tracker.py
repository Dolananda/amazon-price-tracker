from unittest.mock import Mock, patch

from tracker import get_data, sanitize_filename

SAMPLE_HTML = """
<html>
  <body>
    <span id="productTitle"> Example Wireless Mouse </span>
    <span class="a-price-whole">1,299</span>
  </body>
</html>
"""

HTML_WITHOUT_PRICE = """
<html>
  <body>
    <span id="productTitle">No Price Here</span>
  </body>
</html>
"""


def test_sanitize_filename_strips_invalid_characters():
    assert sanitize_filename('Some/Product:Name?*<>|"') == "SomeProductName"


def test_sanitize_filename_truncates_long_names():
    assert len(sanitize_filename("x" * 100)) == 40


@patch("tracker.requests.get")
def test_get_data_parses_title_and_price(mock_get):
    mock_response = Mock()
    mock_response.content = SAMPLE_HTML.encode("utf-8")
    mock_get.return_value = mock_response

    title, price = get_data("https://www.amazon.in/dp/FAKE123")

    assert title == "Example Wireless Mouse"
    assert price == 1299.0


@patch("tracker.requests.get")
def test_get_data_returns_none_when_price_missing(mock_get):
    mock_response = Mock()
    mock_response.content = HTML_WITHOUT_PRICE.encode("utf-8")
    mock_get.return_value = mock_response

    title, price = get_data("https://www.amazon.in/dp/FAKE123")

    assert title is None
    assert price is None


@patch("tracker.requests.get")
def test_get_data_handles_request_exception(mock_get):
    mock_get.side_effect = Exception("network error")

    title, price = get_data("https://www.amazon.in/dp/FAKE123")

    assert title is None
    assert price is None
