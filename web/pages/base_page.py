# Import class Page dan fungsi expect dari Playwright sync API
from playwright.sync_api import Page, expect


# Definisi class BasePage — class induk untuk semua Page Object
class BasePage:
    # Constructor: menerima instance Playwright Page dan menyimpannya sebagai atribut
    def __init__(self, page: Page):
        self.page = page  # Simpan referensi halaman browser untuk digunakan oleh child class

    # Method navigasi: membuka URL yang diberikan di browser
    def navigate_to(self, url: str):
        self.page.goto(url)  # Perintahkan browser untuk membuka URL target

    # Method wait: menunggu sampai URL browser mengandung substring tertentu
    def wait_for_url_contains(self, substring: str, timeout: int = 10000):
        # Gunakan glob pattern (**/*substring*) untuk mencocokkan URL, timeout default 10 detik
        self.page.wait_for_url(f"**/*{substring}*", timeout=timeout)
