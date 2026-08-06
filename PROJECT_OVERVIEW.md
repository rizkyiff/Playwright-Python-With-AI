# 📖 PROJECT OVERVIEW & ARCHITECTURE GUIDE

Proyek ini adalah **Framework Otomatisasi Pengujian Web (Web Test Automation Framework)** tingkat enterprise yang dirancang untuk menguji aplikasi web **eSuite (https://esuite.edot.id)**.

---

## 🎯 Ringkasan Utama Proyek

Framework ini dibangun menggunakan **Python 3.10+**, **Playwright**, **Pytest**, **Allure Report**, **Pydantic**, **Faker**, dan terintegrasi dengan **AI Data Generator**, **AI Failure Triage**, serta **Pipeline CI/CD GitHub Actions**.

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
   - **Tier 1** (`@pytest.mark.tier1`): Verifikasi navigasi dasar dan elemen kunci halaman (login, dashboard).
   - **Tier 2** (`@pytest.mark.tier2`): Verifikasi mendalam bidang-demi-bidang (*field-by-field*) dari data yang disimpan di UI, diikuti oleh alur pembersihan (*cleanup / delete*).

5. **Parallel Execution Support**:
   Menggunakan `pytest-xdist` untuk menjalankan tes secara parallel. Login fixture dilindungi `FileLock` agar aman dari race condition antar worker.

6. **CI/CD & Live Reporting**:
   Setiap perubahan kode di-push ke GitHub, pipeline **GitHub Actions** (`.github/workflows/web_automation.yml`) akan menjalankan tes, mengompilasi laporan Allure lengkap dengan tren riwayat pengujian, dan mempublikasikannya secara otomatis ke **GitHub Pages** di branch `gh-pages`.

---

## 📁 Struktur Direktori & Fungsi Berkas Kode

```text
.
├── ai/                               # AI Module Layer
│   ├── schemas.py                    # Pydantic schema model (CompanyData)
│   ├── generated_data.py            # AI data generator via OpenAI-compatible API
│   └── failure_triage.py            # AI failure analysis & heuristic diagnostics
│
├── web/
│   ├── pages/                       # Page Object Model (POM) Layer
│   │   ├── base_page.py             # Base class — navigate_to(), wait_for_url_contains()
│   │   ├── login_page.py            # Login 2-step — login(email, password, base_url)
│   │   ├── dashboard_page.py        # Dashboard — assert_loaded() ["Welcome Back,"]
│   │   ├── companies_page.py        # Companies — open(), click_add_company(), search_company()
│   │   ├── company_form_page.py     # Wizard 3-step — complete_register_company_wizard(), delete_created_company()
│   │   └── company_detail_page.py   # Tier 2 — assert_company_detail_matches(), delete_company()
│   │
│   ├── data/
│   │   └── test_data_factory.py     # Data factory — get_company_data(), generate_deterministic_company_data()
│   │
│   ├── tests/                       # Test Scenarios Layer
│   │   ├── test_login.py            # Tier 1: test_login_success()
│   │   └── test_company.py          # Tier 2: test_create_company_and_verify_detail()
│   │
│   └── conftest.py                  # Fixtures: logged_in_state(), pytest_runtest_makereport()
│
├── .github/workflows/
│   └── web_automation.yml           # CI/CD pipeline → Allure deploy ke gh-pages
│
├── .env / .env.example              # Environment variables
├── pytest.ini                       # Pytest runner config & custom markers
├── requirements.txt                 # Python dependencies
├── AI_USAGE.md                      # Dokumentasi penggunaan AI
├── PROJECT_OVERVIEW.md              # Dokumen ini
└── README.md                        # Quick start & execution guide
```

---

## 🔧 Detail Fungsi per File

### `web/pages/base_page.py` — Base Class

Class induk untuk semua Page Object. Menyediakan method dasar yang diwarisi.

| Method | Parameter | Keterangan |
|--------|-----------|------------|
| `__init__(page)` | `page: Page` | Menyimpan instance Playwright `Page` |
| `navigate_to(url)` | `url: str` | Navigasi ke URL menggunakan `page.goto()` |
| `wait_for_url_contains(substring, timeout)` | `substring: str`, `timeout: int = 10000` | Menunggu URL saat ini mengandung substring tertentu (timeout default 10 detik) |

---

### `web/pages/login_page.py` — Login Page (2-Step Auth)

Mengelola seluruh alur autentikasi eSuite yang bersifat 2-step.

| Method | Parameter | Keterangan |
|--------|-----------|------------|
| `__init__(page)` | `page: Page` | Inisialisasi locator: `use_email_btn`, `username_input`, `password_input`, `login_button` |
| `login(email, password, base_url)` | `email: str`, `password: str`, `base_url: str` | **Step 1**: Buka `base_url` → klik "Use Email or Username" → isi email → klik "Log In". **Step 2**: Isi password → klik "Log In" |

**Locators yang digunakan:**
- `page.get_by_text("Use Email or Username")` — tombol pilihan metode login
- `input[name="username"]` — field email/username
- `input[name="password"]` — field password
- `button[role="button", name="Log In"]` — tombol submit

---

### `web/pages/dashboard_page.py` — Dashboard Verification

Verifikasi halaman dashboard berhasil dimuat setelah login.

| Method | Parameter | Keterangan |
|--------|-----------|------------|
| `__init__(page)` | `page: Page` | Inisialisasi locator `greeting` = teks "Welcome Back," |
| `assert_loaded()` | — | Memastikan greeting "Welcome Back," **visible** dalam 15 detik. Jika tidak muncul → test FAIL |

---

### `web/pages/companies_page.py` — Companies List

Mengelola navigasi dan interaksi pada halaman daftar perusahaan.

| Method | Parameter | Keterangan |
|--------|-----------|------------|
| `__init__(page)` | `page: Page` | Inisialisasi locator menu Companies, tombol Add Company, dan search input |
| `open()` | — | Klik menu navigasi "Companies" untuk membuka halaman daftar |
| `click_add_company()` | — | Tunggu tombol "Add Company" visible (10s), lalu klik untuk membuka form wizard |
| `search_company(company_name)` | `company_name: str` | Isi field pencarian dengan nama perusahaan lalu tekan Enter |
| `open_company_manage(company_name)` | `company_name: str` | Cari perusahaan → klik tombol "Manage" pada baris yang ditemukan |

---

### `web/pages/company_form_page.py` — Company Registration Wizard (3-Step)

Menangani seluruh proses pengisian wizard registrasi perusahaan baru.

| Method | Parameter | Keterangan |
|--------|-----------|------------|
| `complete_register_company_wizard(data, sample_doc_path)` | `data: dict`, `sample_doc_path: str = None` | Mengisi wizard 3 langkah secara berurutan (lihat detail di bawah) |
| `delete_created_company(company_name)` | `company_name: str` | Menghapus perusahaan dari halaman /companies (Manage → Delete → Agree → Confirm → verify not visible) |

**Detail `complete_register_company_wizard()` — 3 Step:**

**Step 1 — Basic Info & Location:**
- Isi nama perusahaan menggunakan `press_sequentially()` (simulasi ketik per karakter, memicu event input)
- Isi email, telepon (strip leading `0` karena field sudah pakai prefix `+62`)
- Pilih Industry Type, Company Type, Language dari dropdown combobox
- Isi alamat, pilih Country → Province → City → District → Sub District (cascading dropdown)
- Province menggunakan search filter (4 karakter pertama) untuk akurasi
- Klik "Next"

**Step 2 — Upload Legal Document:**
- Klik "+ Add Document" → pilih "Identification Card"
- Upload file via `input[type='file']` (default: `web/data/1.png`)
- Klik "Submit Document" → klik "Next"

**Step 3 — Legal Address & Policy Agreement:**
- Isi Branch Name (default: "Cabang Utama") jika kosong
- Isi alamat legal + dropdown wilayah (sama seperti Step 1)
- Centang `#select-all` (module agreement) — **loop max 10x** sampai tombol "Register" enabled
- Klik "Register"
- Tunggu redirect ke `/companies` → klik nama perusahaan yang baru dibuat

**Detail `delete_created_company()` — Cleanup Flow:**
1. Navigasi ke `/companies` jika belum di sana
2. Klik "Manage" pada card perusahaan (XPath: ancestor traversal)
3. Klik "Delete"
4. Centang "I understand & agree to delete"
5. Klik "Confirm"
6. Verifikasi perusahaan **tidak visible lagi** di UI (`expect(...).not_to_be_visible()`)

---

### `web/pages/company_detail_page.py` — Tier 2 Field-by-Field Verification

Memverifikasi data yang tersimpan di UI secara mendalam (bukan sekadar cek toast success).

| Method | Parameter | Keterangan |
|--------|-----------|------------|
| `assert_company_detail_matches(company_data)` | `company_data: dict` | Verifikasi 7 field: company_name, email, phone, street_address, postal_code, industry_type, company_type |
| `delete_company()` | — | Alternatif cleanup via halaman detail (klik Delete → Confirm) |

**Field yang diverifikasi di `assert_company_detail_matches()`:**

| # | Field | Cara Verifikasi |
|---|-------|-----------------|
| 1 | `company_name` | `expect(get_by_text(name)).to_be_visible()` — **wajib visible** (hard assert) |
| 2 | `email` | `get_by_text(email).is_visible()` → jika visible → assert visible |
| 3 | `phone` | `get_by_text(phone).is_visible()` → jika visible → assert visible |
| 4 | `street_address` | `get_by_text(address).is_visible()` → jika visible → assert visible |
| 5 | `postal_code` | `get_by_text(postal).is_visible()` → jika visible → assert visible |
| 6 | `industry_type` | `get_by_text(industry).is_visible()` → jika visible → assert visible |
| 7 | `company_type` | `get_by_text(type).is_visible()` → jika visible → assert visible |

> Field 2-7 menggunakan soft-check pattern: hanya di-assert jika element terlihat di UI (beberapa field mungkin terlipat atau tidak ditampilkan di view tertentu).

---

### `web/data/test_data_factory.py` — Data Factory

Modul penghasil data test perusahaan Indonesia realistis.

| Function | Parameter | Keterangan |
|----------|-----------|------------|
| `generate_deterministic_company_data()` | — | Generate data menggunakan `Faker("id_ID")`: nama perusahaan "PT QA {nama} {suffix}" (max 30 char), email, telepon 08xxx, alamat, wilayah dari pool `INDONESIAN_REGIONS`. Validasi via `CompanyData` Pydantic model. |
| `get_company_data()` | — | **Entry point utama.** Cek `AI_API_KEY` → jika ada, panggil `generate_ai_company_data()` dari `ai/generated_data.py` → jika error, fallback ke `generate_deterministic_company_data()`. Jika tidak ada API key, langsung Faker. Print data yang digunakan ke console. |

**Pool wilayah (`INDONESIAN_REGIONS`):**
- DKI Jakarta → Jakarta Utara → Kelapa Gading → Kelapa Gading Barat (14240)
- DKI Jakarta → Jakarta Selatan → Mampang Prapatan → Kuningan Barat (12710)

---

### `ai/schemas.py` — Pydantic Schema Validation

| Class | Keterangan |
|-------|------------|
| `CompanyData(BaseModel)` | Model validasi data perusahaan. Fields: `company_name` (max 30), `email`, `phone`, `industry_type` (default: "Retail"), `company_type` (default: "Importer/Exporter"), `language` (default: "Indonesia"), `street_address`, `country` (default: "Indonesia"), `province`, `city`, `district`, `zone`, `postal_code`, `branch_name` (max 30, default: "Cabang Utama") |

Digunakan oleh kedua generator (AI dan Faker) untuk memvalidasi bahwa data output memenuhi format yang benar sebelum dipakai di test.

---

### `ai/generated_data.py` — AI Data Generator

| Function | Parameter | Keterangan |
|----------|-----------|------------|
| `generate_ai_company_data(api_key)` | `api_key: str` | Mengirim prompt terstruktur ke AI API (OpenAI-compatible), memaksa output `json_object`, lalu validasi result dengan `CompanyData` Pydantic. Truncate nama perusahaan ke max 30 char. |

**Konfigurasi:** `AI_BASE_URL` (default: `https://ai.sumopod.com/v1`), `AI_MODEL` (default: `gpt-4o-mini`), temperature `0.7`.

---

### `ai/failure_triage.py` — AI Failure Triage

| Function | Parameter | Keterangan |
|----------|-----------|------------|
| `triage_failure(exception_info)` | `exception_info: str` | Menganalisis stack trace kegagalan test. Jika `AI_API_KEY` ada → kirim ke AI untuk diagnostic 2-bullet root cause. Jika tidak → gunakan heuristic rules berdasarkan pattern exception. |

**Heuristic rules (tanpa AI):**
| Exception Pattern | Root Cause | Fix Recommendation |
|-------------------|------------|-------------------|
| `KeyError` | Key dictionary salah | Cek typo pada nama key |
| `TimeoutError` | Locator timeout | Cek visibility element / XPath |
| `AssertionError` | Assertion gagal | Inspect expected vs actual DOM |
| Lainnya | General exception | Inspect error log terakhir |

---

### `web/conftest.py` — Fixtures & Hooks

#### Fixture: `browser_context_args` (scope: session)
Mengatur viewport default semua browser context ke `1440x900`.

#### Fixture: `auth_state_path` (scope: session)
Mengembalikan path file auth state (`.web_auth/state.json`).

#### Fixture: `logged_in_state` (scope: session)
**Ini adalah core fixture untuk authentication.** Mengelola login sekali per sesi dan menyimpan cookies/token.

```
┌─────────────────────────────────────────────────────┐
│                logged_in_state()                     │
│                                                     │
│  1. Buat folder .web_auth/ jika belum ada            │
│  2. Acquire FileLock (auth.lock)                     │
│     ├─ .web_auth/state.json SUDAH ADA?              │
│     │   └── YES → return path (pakai cache) ◀─────  │
│     │   └── NO  → lanjut login ↓                    │
│     │                                               │
│     │  3. Baca credential dari env (.env)            │
│     │  4. Launch Chromium browser                    │
│     │  5. LoginPage.login(email, password, url)     │
│     │  6. DashboardPage.assert_loaded()             │
│     │  7. context.storage_state() → state.json      │
│     │  8. Close browser                             │
│     └── return path ke state.json                   │
└─────────────────────────────────────────────────────┘
```

#### Hook: `pytest_runtest_makereport` (hookwrapper)
Dipanggil otomatis oleh Pytest setelah setiap test selesai.

```
Test SELESAI → report.failed?
   ├── YES:
   │   ├── 1. Import ai.failure_triage.triage_failure()
   │   ├── 2. Analisis traceback → attach ke Allure ("AI Failure Triage Analysis")
   │   └── 3. Capture screenshot full page → attach ke Allure ("failure_screenshot")
   └── NO: skip (tidak ada aksi)
```

---

## 🔐 Mekanisme Login: Dengan Cache vs Tanpa Cache

### Scenario 1: Login TANPA Cache (First Run)

Terjadi ketika **file `.web_auth/state.json` BELUM ADA** (pertama kali run, atau setelah dihapus manual).

```
pytest web/tests ...
       │
       ▼
 logged_in_state() fixture dipanggil
       │
       ▼
 .web_auth/state.json ada? → TIDAK
       │
       ▼
 ┌── FULL LOGIN FLOW ──────────────────────────────┐
 │ 1. Launch Chromium browser (headless/headed)     │
 │ 2. Buka https://esuite.edot.id                  │
 │ 3. Klik "Use Email or Username"                 │
 │ 4. Isi email → klik "Log In"                    │
 │ 5. Isi password → klik "Log In"                 │
 │ 6. Tunggu dashboard "Welcome Back," visible     │
 │ 7. Simpan cookies + token → state.json          │
 │ 8. Close browser                                │
 └──────────────────────────────────────────────────┘
       │
       ▼
 Return path ".web_auth/state.json"
       │
       ▼
 Test menggunakan: browser.new_context(storage_state=path)
 → Browser langsung dalam keadaan ter-login (ada cookies)
```

**Kapan terjadi:**
- Pertama kali jalankan test
- Setelah menghapus folder `.web_auth/` (atau file `state.json` di dalamnya)
- Session/token expired (perlu hapus manual `state.json` lalu re-run)

### Scenario 2: Login DENGAN Cache (Subsequent Runs)

Terjadi ketika **file `.web_auth/state.json` SUDAH ADA** dari run sebelumnya.

```
pytest web/tests ...
       │
       ▼
 logged_in_state() fixture dipanggil
       │
       ▼
 .web_auth/state.json ada? → YA ✓
       │
       ▼
 SKIP LOGIN ← Langsung return path
       │
       ▼
 Test menggunakan: browser.new_context(storage_state=path)
 → Cookies/token dari file langsung di-load ke browser
 → TIDAK ada proses login UI (lebih cepat)
```

**Keuntungan:**
- Test lebih cepat (skip login ~5-10 detik per session)
- Tidak membebani server dengan request login berulang
- Konsisten — semua test share session yang sama

### Posisi File Cache

```
📁 project root/
└── 📁 .web_auth/                    ← folder ini auto-created
    └── 📄 state.json                ← cookies + localStorage + sessionStorage
```

**Isi `state.json`** (contoh format):
```json
{
  "cookies": [
    {"name": "auth_token", "value": "eyJ...", "domain": "esuite.edot.id", ...},
    {"name": "session_id", "value": "abc123", ...}
  ],
  "origins": [
    {
      "origin": "https://esuite.edot.id",
      "localStorage": [...],
      "sessionStorage": [...]
    }
  ]
}
```

### Cara Force Re-Login (Hapus Cache)

```powershell
# Hapus file state.json saja
Remove-Item .web_auth/state.json

# Atau hapus seluruh folder
Remove-Item -Recurse .web_auth/

# Run ulang test → akan login fresh
pytest web/tests --alluredir=allure-results
```

### Parallel Login Safety (FileLock)

Saat menggunakan `pytest-xdist` (`-n 2` atau `-n auto`), multiple worker bisa saja mencoba login bersamaan. Framework menggunakan `FileLock` untuk mencegah race condition:

```
Worker 1: Acquire lock → state.json belum ada → LOGIN → simpan state.json → release lock
Worker 2: Acquire lock → state.json SUDAH ADA → skip login → return path → release lock
Worker 3: Acquire lock → state.json SUDAH ADA → skip login → return path → release lock
```

Lock file disimpan di temp directory Pytest: `{tmp_path}/../auth.lock`

---

## 📊 Allure Report — Setup & Alur

### Setup Lokal

**Dependencies (sudah di `requirements.txt`):**
```
allure-pytest>=2.13.0
```

**Install Allure CLI (untuk generate/serve report):**
```powershell
# Via Scoop (Windows)
scoop install allure

# Atau download manual: https://github.com/allure-framework/allure2/releases
# Membutuhkan Java Runtime (JRE 8+)
```

### Alur Data Allure

```
pytest web/tests --alluredir=allure-results
       │
       ├── Setiap test menghasilkan file JSON di allure-results/
       │   ├── {test-uuid}-result.json     (hasil test: pass/fail/skip)
       │   ├── {test-uuid}-attachment.*    (screenshot, text, dll)
       │   └── ...
       │
       ▼
allure serve allure-results     (atau: allure generate → allure open)
       │
       ▼
 ┌── Browser terbuka ────────────────────────────────┐
 │  📊 Allure Report                                 │
 │  ├── Overview (pass/fail summary, duration)       │
 │  ├── Suites (test_login.py, test_company.py)     │
 │  ├── Graphs (trend, severity, duration)          │
 │  ├── Timeline (parallel execution timeline)      │
 │  └── Per-test detail:                            │
 │      ├── Steps & substeps                        │
 │      ├── Attachments:                            │
 │      │   ├── "Company test data used" (text)     │
 │      │   ├── "failure_screenshot" (PNG)          │
 │      │   └── "AI Failure Triage Analysis" (text) │
 │      └── Log output                              │
 └───────────────────────────────────────────────────┘
```

### Attachment yang otomatis di-attach ke Allure:

| Attachment Name | Tipe | Kapan Di-attach | Sumber |
|-----------------|------|-----------------|--------|
| `Company test data used` | TEXT | Setiap run `test_company.py` | `test_company.py` → `allure.attach()` |
| `failure_screenshot` | PNG | Hanya saat test FAIL | `conftest.py` → hook `pytest_runtest_makereport` |
| `AI Failure Triage Analysis` | TEXT | Hanya saat test FAIL | `conftest.py` → hook → `triage_failure()` |

### Generate & Buka Report Lokal

```powershell
# Opsi 1: Serve langsung (buka browser otomatis, recommended)
allure serve allure-results

# Opsi 2: Generate ke folder statis lalu buka
allure generate allure-results -o allure-report --clean
allure open allure-report
```

---

## ⚙️ GitHub Actions CI/CD — Penjelasan YAML

File: `.github/workflows/web_automation.yml`

### Trigger Events

```yaml
on:
  push:
    branches: [ main ]        # Setiap push ke branch main
  pull_request:
    branches: [ main ]        # Setiap PR ke branch main
  workflow_dispatch:           # Bisa di-trigger manual dari UI GitHub
  schedule:
    - cron: '0 1 * * *'       # Daily scheduled run jam 01:00 UTC (08:00 WIB)
```

### Permissions

```yaml
permissions:
  contents: write    # Untuk push ke gh-pages branch
  pages: write       # Untuk publish GitHub Pages
  id-token: write    # OIDC token untuk deployment
```

### Step-by-Step Pipeline

| Step | Nama | Apa yang Dilakukan |
|------|------|--------------------|
| 1 | **Checkout Repository Code** | `actions/checkout@v4` — clone repo ke runner |
| 2 | **Set up Python** | `actions/setup-python@v5` — install Python 3.10 dengan pip caching |
| 3 | **Install Python Dependencies** | `pip install -r requirements.txt` — install semua library |
| 4 | **Install Playwright Browsers** | `playwright install --with-deps chromium` — download Chromium + system deps (libglib, libnss, dll) |
| 5 | **Run Web Automation Tests** | `pytest web/tests --alluredir=allure-results` — jalankan semua test, output ke allure-results/ |
| 6 | **Install Allure CLI & Java** | Install JRE + download Allure 2.29.0 tarball → link ke `/usr/local/bin/allure` |
| 7 | **Get Previous Allure History** | Checkout branch `gh-pages` ke `gh-pages-dir/` — ambil data history trend dari report sebelumnya |
| 8 | **Generate Allure Report** | Copy history → `allure generate` — buat report HTML lengkap dengan grafik trend historis |
| 9 | **Deploy to GitHub Pages** | `peaceiris/actions-gh-pages@v4` — push folder `allure-report/` ke branch `gh-pages` → live di GitHub Pages |

### Environment Variables (Secrets)

```yaml
env:
  ESUITE_BASE_URL: ${{ secrets.ESUITE_BASE_URL || 'https://esuite.edot.id' }}
  ESUITE_EMAIL:    ${{ secrets.ESUITE_EMAIL || 'it.qa@edot.id' }}
  ESUITE_PASSWORD: ${{ secrets.ESUITE_PASSWORD || 'it.QA2025' }}
  AI_API_KEY:      ${{ secrets.AI_API_KEY || '' }}
  HEADLESS:        "true"
```

> Jika secret belum di-set di repository, akan menggunakan default value setelah `||`.

### Alur History Trend

```
Run ke-1:  allure-results/ → generate → allure-report/ → deploy ke gh-pages
Run ke-2:  checkout gh-pages → copy history/ ke allure-results/ → generate (with trend) → deploy
Run ke-3:  checkout gh-pages → copy history/ → generate (trend 3 runs) → deploy
...
```

Ini menghasilkan **grafik trend** di Allure Report yang menunjukkan pass/fail rate dari waktu ke waktu.

---

## 🔄 Alur Eksekusi Skenario Utama (`test_company.py`)

1. **Persiapan Data**: `get_company_data()` → menghasilkan profil perusahaan Indonesia dinamis (AI atau Faker).
2. **Attach ke Allure**: Data test yang digunakan di-attach sebagai teks.
3. **Autentikasi**: Membuka browser dengan `storage_state` login yang sudah dicache.
4. **Verifikasi Dashboard**: `DashboardPage.assert_loaded()` — pastikan "Welcome Back," visible.
5. **Navigasi**: `CompaniesPage.open()` → `click_add_company()`.
6. **Pendaftaran Perusahaan** (3 Step Wizard):
   - **Step 1**: Nama, Email, Telepon, Industry, Company Type, Language, Alamat, Wilayah (Province → City → District → Zone).
   - **Step 2**: Upload dokumen legal (`web/data/1.png`).
   - **Step 3**: Alamat legal, Nama Cabang, centang modul agreement → Register.
7. **Verifikasi Tier 2**: `CompanyDetailPage.assert_company_detail_matches()` — cek 7 field satu per satu.
8. **Cleanup**: `delete_created_company()` — hapus perusahaan → verifikasi tidak visible.

---

## 💻 Cara Eksekusi Pengujian

### 1. Jalankan Seluruh Test Suite
```powershell
pytest web/tests --alluredir=allure-results
```

### 2. Jalankan Per Skenario
```powershell
# Login saja (Tier 1)
pytest web/tests/test_login.py --alluredir=allure-results

# Create company (Tier 2)
pytest web/tests/test_company.py --alluredir=allure-results
```

### 3. Jalankan Per Tier Marker
```powershell
pytest web/tests -m tier1 --alluredir=allure-results
pytest web/tests -m tier2 --alluredir=allure-results
```

### 4. Mode Headed (Debugging)
```powershell
$env:HEADLESS="false"; pytest web/tests --alluredir=allure-results
```

### 5. Parallel Execution
```powershell
# 2 parallel workers
pytest web/tests --alluredir=allure-results -n 2

# Auto-detect CPU cores
pytest web/tests --alluredir=allure-results -n auto

# Grouping per file
pytest web/tests --alluredir=allure-results -n 2 --dist loadfile
```

### 6. Force Re-Login (Hapus Cache)
```powershell
Remove-Item .web_auth/state.json
pytest web/tests --alluredir=allure-results
```

### 7. Generate Allure Report
```powershell
allure serve allure-results
```
