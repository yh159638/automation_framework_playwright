import pytest
from scripts.searchScript import search

@pytest.mark.demo
def test_online_store_search(browser_driver):
    search(browser_driver)
