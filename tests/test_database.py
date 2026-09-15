import database


def test_get_or_create_product_creates_new_product(clean_database):
    product_id = database.get_or_create_product("https://example.com/p1", "Test Product")
    product = database.get_product(product_id)

    assert product is not None
    assert product["url"] == "https://example.com/p1"
    assert product["title"] == "Test Product"
    assert product["target_price"] is None
    assert product["target_alert_sent"] is False


def test_get_or_create_product_reuses_existing_by_url(clean_database):
    first_id = database.get_or_create_product("https://example.com/p1", "Original Title")
    second_id = database.get_or_create_product("https://example.com/p1", "Updated Title")

    assert first_id == second_id
    assert database.get_product(first_id)["title"] == "Updated Title"


def test_price_history_and_stats(clean_database):
    product_id = database.get_or_create_product("https://example.com/p2", "Widget")
    for price in [100, 90, 80, 95, 70]:
        database.save_price_point(product_id, price)

    assert database.get_last_price(product_id) == 70

    stats = database.get_price_stats(product_id)
    assert stats["lowest"] == 70
    assert stats["highest"] == 100
    assert stats["latest"] == 70
    assert stats["checks"] == 5


def test_delete_product_removes_history_too(clean_database):
    product_id = database.get_or_create_product("https://example.com/p3", "Gadget")
    database.save_price_point(product_id, 50)

    database.delete_product(product_id)

    assert database.get_product(product_id) is None
    assert database.get_price_history(product_id) == []


def test_set_target_price_resets_alert_flag(clean_database):
    product_id = database.get_or_create_product("https://example.com/p4", "Thing")
    database.mark_target_alert_sent(product_id, True)

    database.set_target_price(product_id, 499.0)
    product = database.get_product(product_id)

    assert product["target_price"] == 499.0
    assert product["target_alert_sent"] is False
