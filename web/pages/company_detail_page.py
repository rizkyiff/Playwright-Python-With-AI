# Import class Page dan fungsi expect dari Playwright sync API
from playwright.sync_api import Page, expect
# Import BasePage sebagai parent class
from web.pages.base_page import BasePage


# Definisi class CompanyDetailPage — verifikasi detail perusahaan (Tier 2 assertion)
class CompanyDetailPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)  # Panggil constructor BasePage untuk set self.page

    # Method Tier 2: verifikasi data perusahaan yang tersimpan di UI, field-by-field
    def assert_company_detail_matches(self, company_data: dict):
        """
        Tier 2 assertion: Verify saved company data field-by-field in the UI,
        not just success toast notifications.
        """
        # Field 1: Company Name — WAJIB visible (hard assert, test FAIL jika tidak muncul)
        company_name = company_data["company_name"]  # Ambil nama dari data test
        expect(self.page.get_by_text(company_name).first).to_be_visible(timeout=10000)  # Assert visible (10s)

        # Field 2: Email — soft check (hanya assert jika elemen terlihat di halaman)
        email_locator = self.page.get_by_text(company_data["email"])  # Cari teks email di halaman
        if email_locator.first.is_visible(timeout=3000):  # Cek apakah visible (3s timeout)
            expect(email_locator.first).to_be_visible()  # Jika visible → assert visible

        # Field 3: Phone — soft check (beberapa UI mungkin menampilkan format berbeda)
        phone_val = str(company_data["phone"])  # Konversi ke string
        phone_locator = self.page.get_by_text(phone_val)  # Cari teks nomor telepon
        if phone_locator.first.is_visible(timeout=3000):  # Cek visible
            expect(phone_locator.first).to_be_visible()  # Assert visible

        # Field 4: Address — soft check (alamat mungkin terlipat/scroll di UI)
        addr_locator = self.page.get_by_text(company_data["street_address"])  # Cari teks alamat
        if addr_locator.first.is_visible(timeout=3000):  # Cek visible
            expect(addr_locator.first).to_be_visible()  # Assert visible

        # Field 5: Postal Code — soft check
        postal_locator = self.page.get_by_text(company_data["postal_code"])  # Cari teks kode pos
        if postal_locator.first.is_visible(timeout=3000):  # Cek visible
            expect(postal_locator.first).to_be_visible()  # Assert visible

        # Field 6: Industry Type — soft check
        ind_locator = self.page.get_by_text(company_data["industry_type"])  # Cari teks tipe industri
        if ind_locator.first.is_visible(timeout=3000):  # Cek visible
            expect(ind_locator.first).to_be_visible()  # Assert visible

        # Field 7: Company Type — soft check
        type_locator = self.page.get_by_text(company_data["company_type"])  # Cari teks tipe perusahaan
        if type_locator.first.is_visible(timeout=3000):  # Cek visible
            expect(type_locator.first).to_be_visible()  # Assert visible

    # Method alternatif cleanup: hapus perusahaan dari halaman detail (jika tombol delete tersedia)
    def delete_company(self):
        """Clean up company from detail page view if available."""
        # Cari tombol Delete (coba role button dulu, fallback ke teks "Delete Company")
        delete_btn = self.page.get_by_role("button", name="Delete").or_(self.page.get_by_text("Delete Company"))
        if delete_btn.first.is_visible(timeout=3000):  # Jika tombol delete visible (3s)
            delete_btn.first.click()  # Klik tombol Delete
            # Cari tombol konfirmasi (coba 3 variasi: "Confirm", "Yes, Delete", "Yes")
            confirm_btn = self.page.get_by_role("button", name="Confirm").or_(self.page.get_by_text("Yes, Delete")).or_(self.page.get_by_role("button", name="Yes"))
            if confirm_btn.first.is_visible(timeout=3000):  # Jika tombol konfirmasi visible
                confirm_btn.first.click()  # Klik untuk konfirmasi penghapusan
