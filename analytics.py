"""Small, dependency-free analytics helpers shared between the desktop GUI
(gui.py) and the web dashboard (streamlit_app.py)."""


def compute_moving_average(prices, window=3):
    """Return a simple moving average over `prices`, one value per input
    point (using however many preceding points are available for the first
    few entries, so the output is always the same length as the input)."""
    result = []
    for i in range(len(prices)):
        start = max(0, i - window + 1)
        chunk = prices[start : i + 1]
        result.append(sum(chunk) / len(chunk))
    return result
