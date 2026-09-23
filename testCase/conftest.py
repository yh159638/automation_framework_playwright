import logging
import pytest
from playwright.sync_api import sync_playwright

from env.session_config import SessionConfig

@pytest.fixture(scope="function")
def browser_driver():
    logging.info("Launching browser...")
    with sync_playwright() as p:        
        browser = p.chromium.launch(headless=False, args=["--start-maximized"], ignore_default_args=["--enable-automation"])
        context = browser.new_context()
        page = context.new_page()
        logging.info("Browser launched successfully.")
        logging.info("Goto test website.")
        page.goto(SessionConfig.ENV_CONFIG["test_url"])
        yield page
        context.close()
        browser.close()
        