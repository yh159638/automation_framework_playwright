from playwright.sync_api import Page, Locator


class FrontPage:
    def __init__(self, page: Page):
        self.page = page
        self.search_input: Locator = page.locator("//input[@name='search-input']")
        self.search_button: Locator = page.locator("//button[normalize-space()='搜尋']")

    