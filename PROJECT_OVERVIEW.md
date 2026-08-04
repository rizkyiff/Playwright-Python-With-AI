# 📖 PROJECT OVERVIEW & ARCHITECTURE GUIDE

Proyek ini adalah **Framework Otomatisasi Pengujian Web (Web Test Automation Framework)** tingkat enterprise yang dirancang untuk menguji aplikasi web **eSuite (https://esuite.edot.id)**.

---

## 🎯 Ringkasan Utama Proyek

Framework ini dibangun menggunakan **Python 3.10+**, **Playwright**, **Pytest**, **Allure Report**, **Pydantic**, **Faker**, dan terintegrasi dengan **AI Data Generator** serta **Pipeline CI/CD GitHub Actions**.

- **Target Aplikasi**: eSuite Web Application (`https://esuite.edot.id`)
- **Live Allure Report (GitHub Pages)**: [https://rizkyiff.github.io/Playwright-Python-With-AI/](https://rizkyiff.github.io/Playwright-Python-With-AI/)
- **Repository GitHub**: [https://github.com/rizkyiff/Playwright-Python-With-AI](https://github.com/rizkyiff/Playwright-Python-With-AI)

---

## 🏗️ Arsitektur & Pola Desain (*Design Patterns*)

1. **Page Object Model (POM)**:
   Mengisolasi kode penemu elemen (*locators*) dan alur interaksi antarmuka ke dalam class halaman tersendiri (`web/pages/`), sehingga skenario tes di `web/tests/` tetap bersih, terbaca, dan mudah dipelihara.

2. **AI-Driven & Deterministic Data Factory**:
   Data uji profil perusahaan Indonesia dibuat secara dinamis menggunakan **AI (OpenAI API)** yang divalidasi oleh **Pydantic JSON Schema** (`ai/schemas.py`). Jika API key tidak dikonfigurasi/expired, sistem secara otomatis (*graceful fallback*) beralih ke generator **Faker** tanpa menghentikan eksekusi tes.

3. **Session Authentication Caching (`storage_state`)**:
   Login dilakukan **1 kali saja per sesi pengujian** melalui fixture Pytest (`web/conftest.py`), lalu cookie/token disimpan ke `.web_auth/state.json`. Skenario tes lain langsung menggunakan state ini tanpa perlu mengulang proses login dari awal.

4. **Pengujian Bertingkat (*Tiered Verification*)**:
   - **Tier 1**: Verifikasi navigasi dasar dan elemen kunci halaman.
   - **Tier 2**: Verifikasi mendalam bidang-demi-bidang (*field-by-field*) dari data yang disimpan di UI, diikuti oleh alur pembersihan (*cleanup / delete*).

5. **CI/CD & Live Reporting**:
   Setiap perubahan kode di-push ke GitHub, pipeline **GitHub Actions** (`.github/workflows/web_automation.yml`) akan menjalankan tes, mengompilasi laporan Allure lengkap dengan tren riwayat pengujian, dan mempublikasikannya secara otomatis ke **GitHub Pages** di branch `gh-pages`.

---

## 📁 Struktur Direktori & Fungsi Berkas Kode

```text
.
├── ai/
│   ├── schemas.py                   # Model Pydantic (CompanyData) untuk validasi struktur data uji
│   ├── generated_data.py            # Generator data AI berbasis prompt JSON & logger transparan
│   └── failure_triage.py            # Helper analisis otomatis penyebab kegagalan tes
│
├── web/
│   ├── pages/                       # Layer Page Object Model (POM)
│   │   ├── base_page.py             # Base class pembungkus metode dasar Playwright
│   │   ├── login_page.py            # Locators & alur autentikasi 2-step eSuite
│   │   ├── dashboard_page.py        # Verifikasi tampilan & greeting Dashboard ("Welcome Back,")
│   │   ├── companies_page.py        # Navigasi & manajemen daftar perusahaan
│   │   ├── company_form_page.py     # Pengisian Wizard Registrasi 3-step & alur Hapus Perusahaan (Delete)
│   │   └── company_detail_page.py   # Tier 2 field-by-field assertion data perusahaan
│   │
│   ├── data/
│   │   └── test_data_factory.py     # Data factory penghasil profil perusahaan Indonesia realistis
│   │
│   ├── tests/                       # Layer Skenario Pengujian
│   │   ├── test_login.py            # Skenario uji login sukses
│   │   └── test_company.py          # Skenario uji E2E create company, Tier 2 verification, & cleanup delete
│   │
│   └── conftest.py                  # Fixture login session state & hook screenshot otomatis saat error
│
├── .github/workflows/
│   └── web_automation.yml           # Pipeline GitHub Actions CI/CD & deploy Allure Report ke gh-pages
│
├── .env / .env.example              # Konfigurasi environment (URL, credential, headless, AI Key)
├── pytest.ini                       # Konfigurasi runner Pytest & live console logging (-s)
├── requirements.txt                 # Dependensi pustaka Python
├── AI_USAGE.md                      # Dokumentasi filosofi penggunaan AI pada pembuatan test data
├── PROJECT_OVERVIEW.md              # Rangkuman lengkap arsitektur dan dokumentasi proyek ini
└── README.md                        # Dokumentasi utama proyek & petunjuk eksekusi
```

---

## 🔄 Alur Eksekusi Skenario Utama (`test_company.py`)

1. **Persiapan Data**: Menghasilkan profil perusahaan Indonesia dinamis (nama perusahaan max 30 karakter, email, telepon, wilayah provinsi/kota berpasangan valid).
2. **Autentikasi**: Membuka browser dengan *storage state* login yang sudah dicache.
3. **Pendaftaran Perusahaan**:
   - **Step 1**: Mengisi Nama Perusahaan, Email, Telepon, Jenis Industri, Tipe Perusahaan, Bahasa, dan Alamat Wilayah (Provinsi -> Kota -> Kecamatan -> Kelurahan).
   - **Step 2**: Mengunggah dokumen legalitas (`web/data/1.png`).
   - **Step 3**: Mengisi Alamat Legal, Nama Cabang, dan mencentang persetujuan modul (`#select-all`) hingga tombol Register aktif.
4. **Verifikasi Tier 2**: Mengecek kebenaran data yang berhasil disimpan di halaman detail perusahaan bidang demi bidang (*field-by-field*).
5. **Penghapusan (*Cleanup*)**:
   - Mengeklik tombol `Manage` pada kartu perusahaan (`//*[contains(text(), '{company_name}')]/ancestor::div[2]//button[text()='Manage']`).
   - Mengeklik tombol `Delete` (`//button[text()='Delete']`).
   - Mencentang checkbox persetujuan hapus (`//*[text()='I understand & agree to delete']/preceding-sibling::*`).
   - Mengeklik `Confirm` (`//button[text()='Confirm']`).
   - Memverifikasi nama perusahaan sudah HAPUS / TIDAK VISIBLE di UI (`expect(...).not_to_be_visible()`).

---

## 💻 Cara Eksekusi Pengujian

### 1. Jalankan Pengujian Lokal (Headed Mode)
```powershell
pytest web/tests/test_company.py --headed
```

### 2. Jalankan Spesifik Skenario dengan Output Konsol Lengkap
```powershell
pytest web/tests/test_company.py -k "test_create_company" -s
```

### 3. Generate Allure Report Lokal
```powershell
pytest web/tests --alluredir=allure-results
allure serve allure-results
```
