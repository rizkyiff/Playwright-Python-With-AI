# Import class Page dan fungsi expect dari Playwright sync API
from playwright.sync_api import Page, expect
# Import BasePage sebagai parent class (inheritance)
from web.pages.base_page import BasePage


# Definisi class LoginPage — mewarisi BasePage, mengelola alur login 2-step eSuite
class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)  # Panggil constructor BasePage untuk set self.page
        # Locator tombol "Use Email or Username" di landing page login
        self.use_email_btn = page.get_by_text("Use Email or Username")
        # Locator input field username/email (atribut name="username")
        self.username_input = page.locator('input[name="username"]')
        # Locator input field password (atribut name="password")
        self.password_input = page.locator('input[name="password"]')
        # Locator tombol "Log In" (role: button)
        self.login_button = page.get_by_role("button", name="Log In")

    # Method utama login: menjalankan alur autentikasi 2-step eSuite
    def login(self, email: str, password: str, base_url: str):
        self.navigate_to(base_url)  # Buka halaman utama eSuite (dari BasePage)

        # Step 1a: Tunggu tombol "Use Email or Username" muncul (max 15 detik)
        self.use_email_btn.wait_for(state="visible", timeout=15000)
        self.use_email_btn.click()  # Klik untuk memilih metode login via email

        # Step 1b: Tunggu input username muncul (max 10 detik)
        self.username_input.wait_for(state="visible", timeout=10000)
        self.username_input.fill(email)  # Isi field username dengan email
        self.login_button.click()  # Klik "Log In" untuk submit username (lanjut ke step 2)

        # Step 2: Tunggu input password muncul (max 10 detik) — halaman berubah setelah step 1
        self.password_input.wait_for(state="visible", timeout=10000)
        self.password_input.fill(password)  # Isi field password
        self.login_button.click()  # Klik "Log In" untuk submit password dan login
