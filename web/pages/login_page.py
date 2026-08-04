from playwright.sync_api import Page, expect
from web.pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.use_email_btn = page.get_by_text("Use Email or Username")
        self.username_input = page.locator('input[name="username"]')
        self.password_input = page.locator('input[name="password"]')
        self.login_button = page.get_by_role("button", name="Log In")

    def login(self, email: str, password: str, base_url: str):
        self.navigate_to(base_url)

        # Wait for and click 'Use Email or Username' landing option
        self.use_email_btn.wait_for(state="visible", timeout=15000)
        self.use_email_btn.click()

        # Step 1: Fill email / username and click Log In
        self.username_input.wait_for(state="visible", timeout=10000)
        self.username_input.fill(email)
        self.login_button.click()

        # Step 2: Fill password and click Log In
        self.password_input.wait_for(state="visible", timeout=10000)
        self.password_input.fill(password)
        self.login_button.click()
