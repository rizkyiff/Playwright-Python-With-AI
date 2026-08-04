from playwright.sync_api import Page, expect


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate_to(self, url: str):
        self.page.goto(url)

    def wait_for_url_contains(self, substring: str, timeout: int = 10000):
        self.page.wait_for_url(f"**/*{substring}*", timeout=timeout)
