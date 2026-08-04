from playwright.sync_api import Page, expect
from web.pages.base_page import BasePage


class DashboardPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.greeting = page.get_by_text("Welcome Back,")

    def assert_loaded(self):
        expect(self.greeting).to_be_visible(timeout=15000)
