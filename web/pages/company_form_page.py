# Import modul regex untuk pattern matching nama perusahaan
import re
# Import Path untuk mengecek keberadaan file dokumen
from pathlib import Path
# Import class Page dan fungsi expect dari Playwright sync API
from playwright.sync_api import Page, expect
# Import BasePage sebagai parent class
from web.pages.base_page import BasePage

# URL dasar eSuite — digunakan untuk navigasi fallback
BASE_URL = "https://esuite.edot.id"


# Definisi class CompanyFormPage — mengelola wizard registrasi perusahaan 3-step dan alur hapus
class CompanyFormPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)  # Panggil constructor BasePage untuk set self.page

    # Method utama: mengisi seluruh wizard registrasi perusahaan (3 langkah berurutan)
    def complete_register_company_wizard(self, data: dict, sample_doc_path: str = None):
        page = self.page  # Shortcut referensi ke self.page agar kode lebih ringkas

        # ==================== STEP 1: Basic Info & Location ====================

        # Cari input nama perusahaan via XPath (berdasarkan placeholder) — lebih stabil dari role-based locator
        company_name_input = page.locator("//input[@placeholder='Input Company Name']")
        company_name_input.wait_for(state="visible", timeout=15000)  # Tunggu input muncul (max 15s)
        company_name_input.click()  # Klik field untuk fokus
        # press_sequentially() = ketik per karakter (simulasi keyboard nyata), delay 50ms antar huruf
        # Ini lebih reliable daripada fill() karena trigger event input/change di framework React/Vue
        company_name_input.press_sequentially(data["company_name"], delay=50)

        # Isi field email — gunakan role-based locator (lebih readable)
        page.get_by_role("textbox", name="Input Email").click()  # Klik untuk fokus
        page.get_by_role("textbox", name="Input Email").fill(data["email"])  # Isi email dari data test

        # Proses nomor telepon — strip leading '0' karena field sudah pakai prefix country code (+62)
        raw_phone = str(data["phone"])  # Konversi ke string (jaga-jaga jika integer)
        phone_val = raw_phone.lstrip("0") if raw_phone.startswith("0") else raw_phone  # Hapus '0' di depan
        page.get_by_role("textbox", name="Input Phone").click()  # Klik field telepon
        page.get_by_role("textbox", name="Input Phone").fill(phone_val)  # Isi nomor tanpa leading 0

        # Pilih Industry Type dari dropdown combobox
        page.get_by_role("combobox").filter(has_text="Choose Industry Type").click()  # Buka dropdown
        page.get_by_role("option", name=data.get("industry_type", "Retail")).click()  # Pilih opsi (default: Retail)

        # Pilih Company Type dari dropdown combobox
        page.get_by_role("combobox").filter(has_text="Choose Company Type").click()  # Buka dropdown
        page.get_by_role("option", name=data.get("company_type", "Importer/Exporter")).click()  # Pilih opsi

        # Pilih Language dari dropdown combobox
        page.get_by_role("combobox").filter(has_text="Choose Language").click()  # Buka dropdown
        page.get_by_role("option", name=data.get("language", "Indonesia")).click()  # Pilih opsi (default: Indonesia)

        # Isi alamat jalan
        page.get_by_role("textbox", name="Input Address").click()  # Klik field alamat
        page.get_by_role("textbox", name="Input Address").fill(data["street_address"])  # Isi alamat

        # Pilih Country dari dropdown
        page.get_by_role("combobox").filter(has_text="Choose Country").click()  # Buka dropdown negara
        page.get_by_role("option", name=data.get("country", "Indonesia")).click()  # Pilih Indonesia

        # Pilih Province — menggunakan search filter (4 huruf pertama) untuk akurasi di dropdown besar
        page.get_by_role("combobox").filter(has_text="Choose Province").click()  # Buka dropdown provinsi
        prov_search = data.get("province", "DKI JAKARTA")[:4].lower()  # Ambil 4 char pertama untuk search (misal: "dki ")
        page.get_by_role("textbox", name="Search").fill(prov_search)  # Ketik di search filter dropdown
        page.get_by_role("option", name=data.get("province", "DKI JAKARTA")).click()  # Pilih provinsi dari hasil filter

        # Pilih City (cascading — opsi muncul setelah province dipilih)
        page.get_by_role("combobox").filter(has_text="Choose City").click()  # Buka dropdown kota
        page.get_by_role("option", name=data.get("city", "JAKARTA UTARA")).click()  # Pilih kota

        # Pilih District (cascading — opsi muncul setelah city dipilih)
        page.get_by_role("combobox").filter(has_text="Choose District").click()  # Buka dropdown kecamatan
        page.get_by_role("option", name=data.get("district", "KELAPA GADING")).click()  # Pilih kecamatan

        # Pilih Sub District / Zone (cascading — opsi muncul setelah district dipilih)
        page.get_by_role("combobox").filter(has_text="Choose Sub District").click()  # Buka dropdown kelurahan
        page.get_by_role("option", name=data.get("zone", "KELAPA GADING BARAT")).click()  # Pilih kelurahan

        # Klik tombol "Next" untuk lanjut ke Step 2
        page.get_by_role("button", name="Next").click()

        # ==================== STEP 2: Upload Legal Document ====================

        # Tunggu tombol "+ Add Document" visible (max 10s) — tombol ada di step 2
        add_doc_btn = page.get_by_role("button", name="+ Add Document")
        add_doc_btn.wait_for(state="visible", timeout=10000)
        add_doc_btn.click()  # Klik untuk membuka dialog upload dokumen

        # Klik dropdown "Choose Legal Document" dan pilih "Identification Card"
        page.locator("button").filter(has_text="Choose Legal Document").click()  # Buka dropdown tipe dokumen
        page.get_by_role("option", name="Identification Card").click()  # Pilih tipe: KTP/ID Card

        # Tentukan file dokumen yang akan diupload
        doc_file = (
            sample_doc_path  # Gunakan path yang diberikan sebagai parameter
            if sample_doc_path and Path(sample_doc_path).exists()  # Jika ada dan file exist
            else "web/data/1.png"  # Fallback ke file default jika tidak diberikan
        )
        # Cari elemen input[type='file'] (hidden file input) untuk upload file
        file_input = page.locator("input[type='file']").first
        if file_input.count() > 0:  # Jika elemen file input ditemukan
            file_input.set_input_files(doc_file)  # Upload file langsung via set_input_files()
        else:
            # Fallback: cari file input di dalam label "Add Legal Document"
            page.get_by_label("Add Legal Document").locator("input[type='file']").set_input_files(doc_file)
        page.get_by_text("Submit Document").click()  # Klik "Submit Document" untuk konfirmasi upload

        # Klik "Next" untuk lanjut ke Step 3
        page.get_by_role("button", name="Next").click()

        # ==================== STEP 3: Legal Address & Policy Agreement ====================

        # Cek dan isi field "Branch Name" jika masih kosong
        branch_input = page.locator("//*[@placeholder='Input Branch Name']")  # Cari via XPath placeholder
        if branch_input.is_visible(timeout=3000):  # Jika field visible (max 3s)
            if not branch_input.input_value():  # Jika field masih kosong (belum terisi otomatis)
                branch_val = data.get("branch_name") or "Cabang Utama"  # Ambil dari data atau default
                branch_input.click()  # Klik field untuk fokus
                branch_input.fill(branch_val)  # Isi nama cabang

        # Isi alamat legal (bisa sama dengan alamat di Step 1)
        page.get_by_role("textbox", name="Input Address").click()
        page.get_by_role("textbox", name="Input Address").fill(data["street_address"])

        # Pilih Country di Step 3 — gunakan .first karena tidak ada filter has_text yang unik
        page.get_by_role("combobox").first.click()  # Buka dropdown pertama (Country)
        page.get_by_role("option", name=data.get("country", "Indonesia")).click()  # Pilih Indonesia

        # Pilih Province (sama seperti Step 1 — dengan search filter)
        page.get_by_role("combobox").filter(has_text="Choose Province").click()
        prov_search = data.get("province", "DKI JAKARTA")[:4].lower()  # 4 char pertama untuk filter
        page.get_by_role("textbox", name="Search").fill(prov_search)  # Ketik search
        page.get_by_role("option", name=data.get("province", "DKI JAKARTA")).click()  # Pilih provinsi

        # Pilih City (cascading)
        page.get_by_role("combobox").filter(has_text="Choose City").click()
        page.get_by_role("option", name=data.get("city", "JAKARTA UTARA")).click()

        # Pilih District (cascading)
        page.get_by_role("combobox").filter(has_text="Choose District").click()
        page.get_by_role("option", name=data.get("district", "KELAPA GADING")).click()

        # Pilih Sub District / Zone (cascading)
        page.get_by_role("combobox").filter(has_text="Choose Sub District").click()
        page.get_by_role("option", name=data.get("zone", "KELAPA GADING BARAT")).click()

        # Centang checkbox "Select All" untuk menyetujui semua modul
        select_all_cb = page.locator("#select-all")  # Checkbox dengan id="select-all"
        register_btn = page.get_by_role("button", name="Register")  # Tombol Register

        # Loop max 10 kali — klik select-all berulang sampai tombol Register ENABLED
        # Diperlukan karena kadang satu klik tidak cukup (race condition UI framework)
        for _ in range(10):
            select_all_cb.click()  # Klik checkbox select-all
            page.wait_for_timeout(500)  # Tunggu 500ms agar UI update
            if not register_btn.is_disabled():  # Cek apakah tombol Register sudah enabled
                break  # Jika sudah enabled, keluar dari loop

        register_btn.click()  # Klik tombol "Register" untuk submit pendaftaran

        # Tunggu redirect otomatis ke halaman /companies setelah registrasi berhasil
        try:
            page.wait_for_url("**/companies**", timeout=10000)  # Tunggu URL berisi "/companies" (max 10s)
        except Exception:
            page.goto(f"{BASE_URL}/companies")  # Fallback: navigasi manual jika redirect gagal

        page.wait_for_load_state("networkidle")  # Tunggu semua request network selesai

        # Cari dan klik nama perusahaan yang baru dibuat di daftar
        company_name = data["company_name"]  # Ambil nama dari data test
        # Gunakan regex untuk mencocokkan nama (re.escape untuk handle karakter spesial)
        company_elem = page.get_by_text(re.compile(re.escape(company_name))).first
        company_elem.wait_for(state="visible", timeout=15000)  # Tunggu elemen muncul (max 15s)
        company_elem.click()  # Klik nama perusahaan untuk membuka halaman detail

    # Method: menghapus perusahaan yang baru dibuat (cleanup untuk menjaga environment bersih)
    def delete_created_company(self, company_name: str):
        page = self.page  # Shortcut referensi

        # 1. Pastikan kita di halaman /companies, navigasi jika belum
        if "/companies" not in page.url:
            page.goto(f"{BASE_URL}/companies")

        # 2. Cari tombol "Manage" pada card perusahaan menggunakan XPath
        # XPath: cari teks company_name → naik 2 level ancestor (div) → cari button "Manage" di dalamnya
        manage_btn = page.locator(
            f"//*[contains(text(), '{company_name}')]/ancestor::div[2]//button[text()='Manage']"
        ).first
        manage_btn.wait_for(state="visible", timeout=10000)  # Tunggu tombol Manage visible (max 10s)
        manage_btn.click()  # Klik tombol Manage untuk membuka menu aksi
        page.wait_for_timeout(1500)  # Tunggu 1.5 detik agar dropdown/menu muncul

        # 3. Klik tombol "Delete" dari menu yang muncul
        delete_btn = page.locator("//button[text()='Delete']").first  # XPath exact match teks "Delete"
        delete_btn.wait_for(state="visible", timeout=10000)  # Tunggu tombol Delete visible
        delete_btn.click()  # Klik Delete

        # 4. Centang checkbox persetujuan hapus — "I understand & agree to delete"
        # XPath: cari teks agreement → ambil elemen sebelumnya (preceding-sibling = checkbox)
        agree_cb = page.locator(
            "//*[text()='I understand & agree to delete']/preceding-sibling::*"
        ).first
        if agree_cb.is_visible(timeout=5000):  # Jika checkbox visible (max 5s)
            agree_cb.click()  # Centang checkbox

        # 5. Klik tombol "Confirm" untuk konfirmasi penghapusan
        confirm_btn = page.locator("//button[text()='Confirm']").first
        if confirm_btn.is_visible(timeout=5000):  # Jika tombol Confirm visible
            confirm_btn.click()  # Klik Confirm

        # 6. Validasi post-delete: pastikan nama perusahaan sudah TIDAK VISIBLE di UI
        page.wait_for_timeout(2000)  # Tunggu 2 detik agar UI update setelah delete
        page.goto(f"{BASE_URL}/companies")  # Refresh halaman companies
        # Assert: elemen dengan teks nama perusahaan harus TIDAK visible (perusahaan sudah terhapus)
        expect(page.locator(f"//*[contains(text(), '{company_name}')]")).not_to_be_visible(timeout=10000)
