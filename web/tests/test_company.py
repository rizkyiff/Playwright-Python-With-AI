# Import modul os untuk membaca environment variable
import os
# Import pytest sebagai test framework
import pytest
# Import allure untuk reporting — attach data ke Allure report
import allure

# Import Page Object classes untuk interaksi dengan halaman-halaman eSuite
from web.pages.dashboard_page import DashboardPage  # Verifikasi dashboard
from web.pages.companies_page import CompaniesPage  # Navigasi ke daftar perusahaan
from web.pages.company_form_page import CompanyFormPage  # Wizard registrasi & delete
from web.pages.company_detail_page import CompanyDetailPage  # Tier 2 field verification
# Import data factory — entry point untuk generate data test (AI atau Faker)
from web.data.test_data_factory import get_company_data


# Decorator: tandai test ini sebagai kategori "web"
@pytest.mark.web
# Decorator: tandai test ini sebagai "tier2" — data mutation & field-level verification
@pytest.mark.tier2
# Definisi test function — parameter 'browser' dan 'logged_in_state' adalah Pytest fixtures
def test_create_company_and_verify_detail(browser, logged_in_state):
    """
    Test Create Company & Tier 2 Field-by-Field Verification & Cleanup:
    1. Generate test data (deterministic fallback or AI schema-validated).
    2. Attach test data used to Allure report.
    3. Login using session storage state.
    4. Navigate to Companies and click Add Company.
    5. Fill Register Company wizard.
    6. Verify created company details field by field (Tier 2 assertion).
    7. Clean up by deleting the created company.
    """
    # Generate data test perusahaan — otomatis pilih AI atau Faker berdasarkan AI_API_KEY
    company_data = get_company_data()

    # Lampirkan data test yang digunakan ke Allure Report (untuk traceability)
    # Sehingga reviewer bisa lihat data apa yang dipakai saat test run
    allure.attach(
        str(company_data),  # Konversi dict ke string untuk ditampilkan
        name="Company test data used",  # Nama attachment di Allure
        attachment_type=allure.attachment_type.TEXT,  # Tipe: plain text
    )

    # Buat browser context baru dengan authentication state dari cache login
    context = browser.new_context(storage_state=logged_in_state)
    page = context.new_page()  # Buka tab baru
    # Navigasi ke base URL eSuite
    page.goto(os.getenv("ESUITE_BASE_URL", "https://esuite.edot.id"))

    # Verifikasi dashboard loaded setelah login via storage state
    dashboard_page = DashboardPage(page)
    dashboard_page.assert_loaded()  # Assert "Welcome Back," visible

    # Navigasi ke halaman Companies dan buka form Add Company
    companies_page = CompaniesPage(page)
    companies_page.open()  # Klik menu "Companies"
    companies_page.click_add_company()  # Klik tombol "Add Company" → buka wizard

    # Isi wizard registrasi perusahaan (3 langkah: Basic Info → Upload Doc → Legal Address)
    sample_doc = "web/data/1.png"  # Path file dokumen legal untuk upload di Step 2
    form_page = CompanyFormPage(page)
    form_page.complete_register_company_wizard(company_data, sample_doc_path=sample_doc)  # Jalankan wizard


    # Tier 2: Verifikasi detail perusahaan yang baru dibuat — cek field-by-field di UI
    detail_page = CompanyDetailPage(page)
    detail_page.assert_company_detail_matches(company_data)  # Assert 7 field sesuai data input

    # Cleanup: Hapus perusahaan yang baru dibuat agar tidak mencemari shared environment
    form_page.delete_created_company(company_data["company_namettd"])  # Delete + verify not visible

    context.close()  # Tutup browser context (cleanup resources)
