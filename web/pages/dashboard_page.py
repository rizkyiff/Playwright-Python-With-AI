# Import class Page dan fungsi expect dari Playwright sync API
from playwright.sync_api import Page, expect
# Import BasePage sebagai parent class
from web.pages.base_page import BasePage


# Definisi class DashboardPage — verifikasi halaman dashboard setelah login berhasil
class DashboardPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)  # Panggil constructor BasePage untuk set self.page
        # Locator teks greeting "Welcome Back," yang muncul di dashboard setelah login
        self.greeting = page.get_by_text("Welcome Back,")

    # Method assertion: pastikan dashboard sudah loaded dengan mengecek greeting visible
    def assert_loaded(self):
        # Expect greeting "Welcome Back," harus visible dalam 15 detik, jika tidak → test FAIL
        expect(self.greeting).to_be_visible(timeout=15000)
