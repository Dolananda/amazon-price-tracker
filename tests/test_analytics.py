from analytics import compute_moving_average


def test_single_value():
    assert compute_moving_average([100]) == [100]


def test_shorter_than_window():
    assert compute_moving_average([100, 200], window=3) == [100, 150]


def test_exact_window():
    assert compute_moving_average([100, 200, 300], window=3) == [100, 150, 200]


def test_window_slides_once_full():
    assert compute_moving_average([100, 200, 300, 400], window=2) == [100, 150, 250, 350]


def test_output_length_matches_input():
    prices = [10, 20, 30, 40, 50, 60]
    assert len(compute_moving_average(prices, window=3)) == len(prices)
