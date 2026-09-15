import database
import exporter


def test_price_history_csv_has_header_and_rows(clean_database):
    product_id = database.get_or_create_product("https://example.com/e1", "Exported Item")
    for price in [100, 90]:
        database.save_price_point(product_id, price)

    csv_text = exporter.price_history_to_csv(product_id)
    lines = csv_text.strip().splitlines()

    assert lines[0] == "timestamp,price"
    assert len(lines) == 3  # header + 2 price points
    assert lines[-1].endswith(",90")


def test_price_history_csv_empty_history(clean_database):
    product_id = database.get_or_create_product("https://example.com/e2", "No History")

    csv_text = exporter.price_history_to_csv(product_id)

    assert csv_text.strip() == "timestamp,price"


def test_watchlist_summary_sorted_by_biggest_drop(clean_database):
    small_drop = database.get_or_create_product("https://example.com/e3", "Small Drop")
    database.save_price_point(small_drop, 100)
    database.save_price_point(small_drop, 95)  # -5%

    big_drop = database.get_or_create_product("https://example.com/e4", "Big Drop")
    database.save_price_point(big_drop, 100)
    database.save_price_point(big_drop, 50)  # -50%

    summary = database.get_watchlist_summary()

    assert summary[0]["title"] == "Big Drop"
    assert summary[0]["drop_from_high_pct"] == -50.0
    assert summary[0]["at_lowest_ever"] is True


def test_watchlist_summary_skips_products_without_history(clean_database):
    database.get_or_create_product("https://example.com/e5", "Never Checked")

    assert database.get_watchlist_summary() == []


def test_watchlist_summary_csv_has_header(clean_database):
    product_id = database.get_or_create_product("https://example.com/e6", "Item")
    database.save_price_point(product_id, 200)

    csv_text = exporter.watchlist_summary_to_csv()
    lines = csv_text.strip().splitlines()

    assert lines[0].startswith("title,url,latest")
    assert len(lines) == 2
