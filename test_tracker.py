from unittest.mock import Mock, patch

import pytest

import tracker
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


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    """Retries use time.sleep() for backoff — skip the actual waiting in tests."""
    monkeypatch.setattr(tracker.time, "sleep", lambda seconds: None)


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
    assert mock_get.call_count == 1  # succeeded first try, no retries needed


@patch("tracker.requests.get")
def test_get_data_returns_none_when_price_missing(mock_get):
    mock_response = Mock()
    mock_response.content = HTML_WITHOUT_PRICE.encode("utf-8")
    mock_get.return_value = mock_response

    title, price = get_data("https://www.amazon.in/dp/FAKE123")

    assert title is None
    assert price is None
    assert mock_get.call_count == tracker.MAX_RETRIES


@patch("tracker.requests.get")
def test_get_data_handles_request_exception(mock_get):
    mock_get.side_effect = Exception("network error")

    title, price = get_data("https://www.amazon.in/dp/FAKE123")

    assert title is None
    assert price is None
    assert mock_get.call_count == tracker.MAX_RETRIES


@patch("tracker.requests.get")
def test_get_data_recovers_after_a_transient_failure(mock_get):
    mock_success = Mock()
    mock_success.content = SAMPLE_HTML.encode("utf-8")
    mock_get.side_effect = [Exception("temporary network blip"), mock_success]

    title, price = get_data("https://www.amazon.in/dp/FAKE123")

    assert title == "Example Wireless Mouse"
    assert price == 1299.0
    assert mock_get.call_count == 2
