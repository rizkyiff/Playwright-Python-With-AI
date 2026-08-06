# Import class Page dan fungsi expect dari Playwright sync API
from playwright.sync_api import Page, expect
# Import BasePage sebagai parent class
from web.pages.base_page import BasePage


# Definisi class CompaniesPage — mengelola halaman daftar perusahaan
class CompaniesPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)  # Panggil constructor BasePage untuk set self.page
        # Locator menu navigasi "Companies" — coba role link dulu, fallback ke teks
        self.companies_menu = page.get_by_role("link", name="Companies").or_(page.get_by_text("Companies"))
        # Locator tombol "Add Company" — coba 3 variasi teks/role untuk fleksibilitas UI
        self.add_company_button = page.get_by_role("button", name="Add Company").or_(page.get_by_text("+ Add Company")).or_(page.get_by_text("Add Company"))
        # Locator input pencarian — cari elemen input dengan placeholder "Search" atau type "search", ambil yang pertama
        self.search_input = page.locator('input[placeholder*="Search"], input[type="search"]').first

    # Method: klik menu navigasi "Companies" untuk membuka halaman daftar
    def open(self):
        self.companies_menu.first.click()  # .first karena locator bisa match lebih dari 1 elemen

    # Method: klik tombol "Add Company" untuk membuka form wizard registrasi
    def click_add_company(self):
        self.add_company_button.first.wait_for(state="visible", timeout=10000)  # Tunggu tombol visible (max 10s)
        self.add_company_button.first.click()  # Klik tombol Add Company

    # Method: isi field pencarian dengan nama perusahaan lalu tekan Enter
    def search_company(self, company_name: str):
        if self.search_input.is_visible(timeout=3000):  # Cek apakah search input ada & visible (3s)
            self.search_input.fill(company_name)  # Isi field pencarian dengan nama perusahaan
            self.page.keyboard.press("Enter")  # Tekan Enter untuk trigger pencarian

    # Method: cari perusahaan lalu klik tombol "Manage" pada baris yang ditemukan
    def open_company_manage(self, company_name: str):
        self.search_company(company_name)  # Panggil method pencarian terlebih dahulu
        # Cari baris tabel (<tr>) yang mengandung teks nama perusahaan, ambil yang pertama
        row = self.page.locator("tr", has_text=company_name).first
        # Cari tombol "Manage" di dalam baris tersebut (role button atau teks)
        manage_btn = row.get_by_role("button", name="Manage").or_(row.get_by_text("Manage"))
        if manage_btn.is_visible(timeout=5000):  # Jika tombol Manage visible (max 5s)
            manage_btn.click()  # Klik tombol Manage
        else:
            # Fallback: klik langsung teks nama perusahaan jika struktur tabel berbeda
            self.page.get_by_text(company_name).first.click()
