# eSuite Web Automation Framework

[![Web Automation CI/CD & Allure Report](https://github.com/rizkyiff/Playwright-Python-With-AI/actions/workflows/web_automation.yml/badge.svg)](https://github.com/rizkyiff/Playwright-Python-With-AI/actions/workflows/web_automation.yml)
[![Live Allure Report](https://img.shields.io/badge/Allure%20Report-Live%20GitHub%20Pages-brightgreen)](https://rizkyiff.github.io/Playwright-Python-With-AI/)

Framework otomatisasi pengujian web untuk **eSuite (https://esuite.edot.id)** menggunakan **Python**, **Playwright**, **Pytest**, **Allure Report**, dan **GitHub Actions CI/CD**.

> 🌐 **Live Allure Report (GitHub Pages)**: [https://rizkyiff.github.io/Playwright-Python-With-AI/](https://rizkyiff.github.io/Playwright-Python-With-AI/)  
> Reports are automatically generated, updated with historical trends, and published to the `gh-pages` branch on every test run!

---

## 📁 Project Structure & Code Utility

Berikut adalah penjelasan lengkap struktur direktori dan kegunaan masing-masing berkas kode dalam proyek ini:

```text
.
├── ai/
│   ├── schemas.py                   # Pydantic schema model untuk meyakinkan data test valid
│   ├── generated_data.py            # Data module wrapper untuk AI / deterministic fallback generator
│   └── failure_triage.py            # Helper analisis otomatis penyebab kegagalan test
│
├── web/
│   ├── pages/                       # Page Object Model (POM) Layer
│   │   ├── base_page.py             # Base class pembungkus interaksi dasar Playwright
│   │   ├── login_page.py            # Locators & alur login 2-step eSuite
│   │   ├── dashboard_page.py        # Verifikasi tampilan & greeting Dashboard ("Welcome Back,")
│   │   ├── companies_page.py        # Navigasi ke menu Companies & pembukaan form registration
│   │   ├── company_form_page.py     # Pengisian wizard registrasi perusahaan
│   │   └── company_detail_page.py   # Tier 2 field-by-field verification & cleanup data
│   │
│   ├── data/
│   │   └── test_data_factory.py     # Data factory penghasil profil perusahaan Indonesia realistis (Faker)
│   │
│   ├── tests/                       # Test Scenarios Layer
│   │   ├── test_login.py            # Skenario uji login sukses (Tier 1 assertion)
│   │   └── test_company.py          # Skenario uji E2E create company, Tier 2 verification, & delete cleanup
│   │
│   └── conftest.py                  # Pytest session fixture login (storage_state) & failure screenshot hook
│
├── .env / .env.example              # Konfigurasi environment (URL, credential, headless mode, API key)
├── pytest.ini                       # Konfigurasi runner Pytest, log options, dan custom markers
├── requirements.txt                 # Dependensi pustaka Python (Playwright, Pytest, Allure, Faker, Pydantic)
├── AI_USAGE.md                      # Panduan & filosofi penggunaan AI pada pembuatan test data
└── README.md                        # Dokumentasi utama proyek & petunjuk eksekusi
```

### Detail Kegunaan Masing-Masing File:

1. **`web/pages/` (Page Object Model Architecture)**
   - [base_page.py](file:///d:/Coding/playwright%20py/web/pages/base_page.py): Menyediakan metode dasar navigasi dan penanganan timeout Playwright yang diwarisi oleh semua class halaman.
   - [login_page.py](file:///d:/Coding/playwright%20py/web/pages/login_page.py): Mengisolasi semua selector tombol "Use Email or Username", input username, input password, dan penanganan alur autentikasi eSuite.
   - [dashboard_page.py](file:///d:/Coding/playwright%20py/web/pages/dashboard_page.py): Memverifikasi elemen dashboard utama dan memastikan greeting `Welcome Back,` muncul sesuai requirement.
   - [companies_page.py](file:///d:/Coding/playwright%20py/web/pages/companies_page.py): Menangani interaksi menu navigasi utama ke halaman daftar Companies dan pencarian data perusahaan.
   - [company_form_page.py](file:///d:/Coding/playwright%20py/web/pages/company_form_page.py): Menangani pengisian berurutan pada Wizard Registration Company (nama perusahaan, email, telepon, jenis industri, tipe perusahaan, alamat, hingga wilayah).
   - [company_detail_page.py](file:///d:/Coding/playwright%20py/web/pages/company_detail_page.py): Melakukan **Tier 2 assertion** mendalam dengan mengecek kebenaran data bidang demi bidang (*field-by-field*) pada halaman detail serta memfasilitasi penataan ulang (*cleanup / delete*).

2. **`web/conftest.py` (Fixtures & Hooks)**
   - `logged_in_state`: Fixture berskala *session* yang melakukan login satu kali di awal pengujian dan menyimpan token/cookie autentikasi ke `.web_auth/state.json`. Test lain tinggal menggunakan *storage state* ini tanpa perlu login ulang.
   - `pytest_runtest_makereport`: Hook Pytest otomatis yang menangkap screenshot halaman (PNG full page) jika terjadi error/failure pada test dan menempelkannya secara transparan ke laporan Allure.

3. **`ai/` & `web/data/` (AI & Data Generator Layer)**
   - [schemas.py](file:///d:/Coding/playwright%20py/ai/schemas.py): Model Pydantic (`CompanyData`) yang memastikan semua bidang data perusahaan (nama, email, telepon, alamat, pos) memenuhi format dan kaidah yang valid sebelum dimasukkan ke dalam test.
   - [test_data_factory.py](file:///d:/Coding/playwright%20py/web/data/test_data_factory.py): Menghasilkan data pengujian unik berbasis profil Indonesia nyata menggunakan `Faker` secara teratur (*deterministic fallback*). Jika `AI_API_KEY` dikonfigurasi, modul ini memanfaatkan model AI untuk membuat variasi data yang lebih kompleks.

4. **`web/tests/` (Skenario Pengujian)**
   - [test_login.py](file:///d:/Coding/playwright%20py/web/tests/test_login.py): Menguji keberhasilan autentikasi dan memvalidasi tampilan dashboard (`@pytest.mark.tier1`).
   - [test_company.py](file:///d:/Coding/playwright%20py/web/tests/test_company.py): Skenario utama `@pytest.mark.tier2` yang mendaftarkan perusahaan baru, memverifikasi seluruh detail bidang, dan menghapus perusahaan yang baru dibuat untuk menjaga kebersihan *shared environment*.

---

## 🚀 Key Features

- **Page Object Model (POM)**: Pemisahan tegas antara locator UI di `web/pages` dan logika skenario di `web/tests`. Tidak ada *raw selector* di dalam file test.
- **Session Authentication**: Menggunakan Playwright `storage_state` (`.web_auth/state.json`) sehingga login hanya dijalankan 1x per sesi pengujian.
- **Strict Data Validation**: Mengintegrasikan Pydantic schema validation untuk memastikan keabsahan data sebelum eksekusi.
- **Tier 2 Field-by-Field Verification**: Memverifikasi setiap kolom data pada detail perusahaan, bukan sekadar mengecek toast pemberitahuan sukses.
- **Automatic Environment Cleanup**: Menghapus kembali data perusahaan buatan di akhir pengujian agar tidak mencemari environment bersama.
- **Allure Screenshot Attachment**: Screenshot kegagalan pengujian otomatis tertempel ke Allure report via hook Pytest.

---

## 🛠️ Quick Start & Execution Guide

### 1. Prerequisites
- Python 3.10+
- Pip & Virtual Environment

### 2. Setup Virtual Environment & Install Dependencies
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

### 3. Environment Variables
Konfigurasi file `.env` (contoh tersedia di `.env.example`):
```env
ESUITE_BASE_URL=https://esuite.edot.id
ESUITE_EMAIL=it.qa@edot.id
ESUITE_PASSWORD=it.QA2025
HEADLESS=true
AI_API_KEY=
```

### 4. Running Tests

Run seluruh test suite dan hasilkan data Allure:
```powershell
.\.venv\Scripts\python.exe -m pytest web/tests --alluredir=allure-results
```

Run test login saja:
```powershell
.\.venv\Scripts\python.exe -m pytest web/tests/test_login.py --alluredir=allure-results
```

Run test create company saja:
```powershell
.\.venv\Scripts\python.exe -m pytest web/tests/test_company.py --alluredir=allure-results
```

Run dalam mode Headed / UI untuk debugging:
```powershell
$env:HEADLESS="false"; .\.venv\Scripts\python.exe -m pytest web/tests --alluredir=allure-results
```

Run berdasarkan tier marker:
```powershell
# Tier 1 saja (login & navigation)
.\.venv\Scripts\python.exe -m pytest web/tests -m tier1 --alluredir=allure-results

# Tier 2 saja (data mutation & field-level verification)
.\.venv\Scripts\python.exe -m pytest web/tests -m tier2 --alluredir=allure-results
```

### 5. Parallel Execution (pytest-xdist)

Framework ini mendukung eksekusi parallel menggunakan `pytest-xdist`. Setiap worker mendapatkan browser context terpisah.

```powershell
# Run dengan 2 parallel workers
.\.venv\Scripts\python.exe -m pytest web/tests --alluredir=allure-results -n 2

# Auto-detect jumlah CPU cores
.\.venv\Scripts\python.exe -m pytest web/tests --alluredir=allure-results -n auto

# Grouping per file (test dalam 1 file tidak dipecah antar worker)
.\.venv\Scripts\python.exe -m pytest web/tests --alluredir=allure-results -n 2 --dist loadfile
```

> ⚠️ **Catatan**: Flag `-s` (live console output) tidak compatible dengan `pytest-xdist`. Saat run parallel, output console per-test akan di-capture dan ditampilkan setelah selesai. Untuk debugging dengan live output, jalankan tanpa `-n`.

### 6. Generate & Open Allure Report

Setelah menjalankan test suite, generate dan buka Allure Report secara lokal:

```powershell
# Generate report statis ke folder allure-report/
allure generate allure-results -o allure-report --clean

# Atau langsung serve & buka di browser (recommended)
allure serve allure-results
```

> 💡 **Allure CLI** membutuhkan Java Runtime (JRE 8+). Install Allure CLI via:
> ```powershell
> # Via Scoop (Windows)
> scoop install allure
>
> # Atau download manual dari https://github.com/allure-framework/allure2/releases
> ```

> 🌐 **Live Report (CI/CD)**: Report otomatis di-generate dan di-publish ke GitHub Pages pada setiap push ke `main`.
> Akses di: [https://rizkyiff.github.io/Playwright-Python-With-AI/](https://rizkyiff.github.io/Playwright-Python-With-AI/)

---

## 📄 Dokumentasi Tambahan

- [AI_USAGE.md](AI_USAGE.md) — Panduan & filosofi penggunaan AI pada framework ini
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) — Arsitektur lengkap & alur eksekusi detail
