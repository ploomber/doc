def test_example():
    assert 1 + 1 == 2


def test_asset(path_to_test_assets):
    assert (
        path_to_test_assets / "test_asset.md"
    ).read_text() == "This is some asset used by the test suite."
