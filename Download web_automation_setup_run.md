# Web Automation Setup & Run Guide

Guide ini menjelaskan cara setup dan menjalankan **web automation eSuite** menggunakan **Playwright + Pytest + Allure**.

> Assignment requirement: web automation wajib menggunakan **Python + Pytest + Playwright**, menerapkan **Page Object Model**, memakai **Allure Report**, tidak menggunakan Selenium, tidak memakai `time.sleep()`, dan tidak menyimpan credential/API key langsung di repository.

---

## 1. Scope Web Automation

Target aplikasi:

```text
https://esuite.edot.id
```

Skenario web yang wajib dibuat:

1. **Login**
   - Login ke eSuite.
   - Assert dashboard greeting `Welcome Back,` tampil.

2. **Create Company**
   - Masuk ke menu **Companies**.
   - Klik **+ Add Company**.
   - Isi wizard **Register Company**.
   - Gunakan test data company dari AI-generated data module atau deterministic fallback.

3. **Verify Company Detail**
   - Buka company melalui **Companies → Manage**.
   - Assert field by field:
     - Company name
     - Industry type
     - Company type
     - Address
     - Postal code
     - Email
     - Phone
   - Ini wajib **Tier 2 assertion**, jadi tidak cukup hanya cek toast sukses.

4. **Clean Up**
   - Delete company yang dibuat di akhir run.
   - Ini penting karena environment yang digunakan adalah shared environment.

---

## 2. Prerequisites

Pastikan sudah install:

- Python 3.10 atau lebih baru
- pip
- Git
- Browser dependencies untuk Playwright
- Allure commandline

Cek versi Python:

```bash
python --version
```

Atau di Linux/macOS/WSL:

```bash
python3 --version
```

---

## 3. Setup Project

Clone repository:

```bash
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_REPOSITORY_FOLDER>
```

Buat virtual environment:

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux / WSL

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

---

## 4. Install Dependencies

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Jika belum ada `requirements.txt`, minimal isi file-nya seperti ini:

```text
pytest
pytest-playwright
playwright
allure-pytest
python-dotenv
pydantic
faker
```

Install browser Playwright:

```bash
playwright install
```

Jika di Linux/WSL dan butuh dependency browser tambahan:

```bash
playwright install --with-deps
```

---

## 5. Install Allure Commandline

### macOS dengan Homebrew

```bash
brew install allure
```

### Windows dengan Scoop

```powershell
scoop install allure
```

### Linux / WSL manual option

Jika package manager tidak tersedia, install Allure commandline sesuai environment kamu, lalu pastikan command ini berhasil:

```bash
allure --version
```

---

## 6. Environment Variables

Jangan hardcode credential langsung di code atau repository.

Buat file `.env.example`:

```bash
ESUITE_BASE_URL=https://esuite.edot.id
ESUITE_EMAIL=it.qa@edot.id
ESUITE_PASSWORD=it.QA2025
HEADLESS=true
AI_API_KEY=
```

> Commit `.env.example`, tetapi jangan commit `.env`.

Buat file `.env` lokal:

```bash
ESUITE_BASE_URL=https://esuite.edot.id
ESUITE_EMAIL=it.qa@edot.id
ESUITE_PASSWORD=it.QA2025
HEADLESS=false
AI_API_KEY=
```

Jika tidak ada `AI_API_KEY`, suite harus otomatis memakai deterministic fallback, misalnya Faker.

---

## 7. Struktur Folder yang Disarankan

```text
project-root/
  web/
    pages/
      login_page.py
      dashboard_page.py
      companies_page.py
      company_form_page.py
      company_detail_page.py
    tests/
      test_login.py
      test_company.py
    data/
      test_data_factory.py
    conftest.py
  ai/
    generated_data.py
    schemas.py
    failure_triage.py
  allure-results/
  requirements.txt
  pytest.ini
  README.md
  AI_USAGE.md
```

---

## 8. Pytest Configuration

File: `pytest.ini`

```ini
[pytest]
addopts = -v
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    web: web automation tests
    tier1: navigation/display assertion tests
    tier2: data mutation and field-level verification tests
```

---

## 9. Playwright Session Strategy

Requirement assignment meminta login dilakukan sekali per session dan auth disimpan menggunakan `storage_state`.

Rekomendasi flow:

1. Test setup login ke eSuite.
2. Simpan auth state ke file lokal, misalnya:

```text
.web_auth/state.json
```

3. Test lain menggunakan `storage_state` tersebut.
4. Folder `.web_auth/` jangan di-commit.

Tambahkan ke `.gitignore`:

```gitignore
.env
.web_auth/
allure-results/
allure-report/
__pycache__/
.pytest_cache/
```

---

## 10. Contoh `conftest.py`

File: `web/conftest.py`

```python
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

BASE_URL = os.getenv("ESUITE_BASE_URL", "https://esuite.edot.id")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
AUTH_DIR = Path(".web_auth")
AUTH_STATE = AUTH_DIR / "state.json"


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1440, "height": 900},
    }


@pytest.fixture(scope="session")
def auth_state_path():
    return str(AUTH_STATE)


@pytest.fixture(scope="session")
def logged_in_state():
    AUTH_DIR.mkdir(exist_ok=True)

    if AUTH_STATE.exists():
        return str(AUTH_STATE)

    email = os.environ["ESUITE_EMAIL"]
    password = os.environ["ESUITE_PASSWORD"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        page.goto(BASE_URL)

        # Keep raw selectors inside page objects in final implementation.
        # This setup example is intentionally minimal. Move this login flow
        # into LoginPage for the real project.
        page.get_by_text("Use Email or Username").click()
        page.get_by_role("textbox").fill(email)
        page.get_by_role("button", name="Next").click()
        page.get_by_role("textbox").fill(password)
        page.get_by_role("button", name="Login").click()
        page.get_by_text("Welcome Back,").wait_for()

        context.storage_state(path=str(AUTH_STATE))
        browser.close()

    return str(AUTH_STATE)
```

> Note: contoh di atas hanya gambaran. Untuk final submission, login flow sebaiknya dipindahkan ke `LoginPage`, karena requirement menyebut locator harus berada di page class, bukan langsung di test file.

---

## 11. Page Object Model Rules

Gunakan Page Object Model untuk semua interaction.

Aturan penting:

- Test file hanya berisi scenario dan assertion.
- Locator harus berada di page class.
- Jangan taruh raw selector di test file.
- Jangan pakai `time.sleep()`.
- Gunakan Playwright auto-waiting dan `expect()`.

Prioritas locator:

1. `data-testid`
2. role + accessible name
3. stable attribute seperti `name`, `id`, atau `aria-*`
4. text sebagai last resort

Jika memakai text sebagai locator, tambahkan comment singkat kenapa locator tersebut dipakai.

---

## 12. Contoh Page Object

File: `web/pages/dashboard_page.py`

```python
from playwright.sync_api import Page, expect


class DashboardPage:
    def __init__(self, page: Page):
        self.page = page
        self.greeting = page.get_by_text("Welcome Back,")

    def assert_loaded(self):
        expect(self.greeting).to_be_visible()
```

File: `web/pages/companies_page.py`

```python
from playwright.sync_api import Page, expect


class CompaniesPage:
    def __init__(self, page: Page):
        self.page = page
        self.companies_menu = page.get_by_role("link", name="Companies")
        self.add_company_button = page.get_by_role("button", name="Add Company")

    def open(self):
        self.companies_menu.click()

    def click_add_company(self):
        self.add_company_button.click()
```

File: `web/pages/company_detail_page.py`

```python
from playwright.sync_api import Page, expect


class CompanyDetailPage:
    def __init__(self, page: Page):
        self.page = page

    def assert_company_detail_matches(self, company_data: dict):
        # Tier 2 assertion: verify saved data field by field, not only success toast.
        expect(self.page.get_by_text(company_data["company_name"])).to_be_visible()
        expect(self.page.get_by_text(company_data["email"])).to_be_visible()
        expect(self.page.get_by_text(company_data["phone"])).to_be_visible()
        expect(self.page.get_by_text(company_data["street_address"])).to_be_visible()
        expect(self.page.get_by_text(company_data["postal_code"])).to_be_visible()
        expect(self.page.get_by_text(company_data["industry_type"])).to_be_visible()
        expect(self.page.get_by_text(company_data["company_type"])).to_be_visible()
```

---

## 13. Contoh Test Login

File: `web/tests/test_login.py`

```python
import os
import pytest
from playwright.sync_api import expect

from web.pages.dashboard_page import DashboardPage


@pytest.mark.web
@pytest.mark.tier1
def test_login_success(browser, logged_in_state):
    context = browser.new_context(storage_state=logged_in_state)
    page = context.new_page()
    page.goto(os.getenv("ESUITE_BASE_URL"))

    dashboard_page = DashboardPage(page)
    dashboard_page.assert_loaded()

    context.close()
```

---

## 14. Contoh Test Create Company & Verify Detail

File: `web/tests/test_company.py`

```python
import os
import pytest
import allure

from web.pages.dashboard_page import DashboardPage
from web.pages.companies_page import CompaniesPage
from web.pages.company_form_page import CompanyFormPage
from web.pages.company_detail_page import CompanyDetailPage
from web.data.test_data_factory import get_company_data


@pytest.mark.web
@pytest.mark.tier2
def test_create_company_and_verify_detail(browser, logged_in_state):
    company_data = get_company_data()

    allure.attach(
        str(company_data),
        name="Company test data used",
        attachment_type=allure.attachment_type.TEXT,
    )

    context = browser.new_context(storage_state=logged_in_state)
    page = context.new_page()
    page.goto(os.getenv("ESUITE_BASE_URL"))

    dashboard_page = DashboardPage(page)
    dashboard_page.assert_loaded()

    companies_page = CompaniesPage(page)
    companies_page.open()
    companies_page.click_add_company()

    form_page = CompanyFormPage(page)
    form_page.complete_register_company_wizard(company_data)

    detail_page = CompanyDetailPage(page)
    detail_page.assert_company_detail_matches(company_data)

    # Cleanup is mandatory because this is a shared environment.
    form_page.delete_created_company(company_data["company_name"])

    context.close()
```

---

## 15. AI-generated Test Data Requirement

Automation harus memakai data company dari AI-generated data module.

Requirement penting:

- AI menghasilkan data bisnis Indonesia yang realistic dan coherent.
- Output AI divalidasi dengan schema sebelum dipakai test.
- Jika output invalid, retry atau fallback.
- Jika tidak ada API key, gunakan deterministic fallback, misalnya Faker.
- Data yang benar-benar dipakai harus di-attach ke Allure.

Contoh field company data:

```json
{
  "company_name": "PT Sinar Maju Otomasi",
  "email": "qa.company@example.com",
  "phone": "081234567890",
  "industry_type": "Retail",
  "company_type": "Distributor",
  "language": "Indonesia",
  "street_address": "Jl. Kemang Raya No. 10",
  "country": "Indonesia",
  "province": "DKI Jakarta",
  "city": "Jakarta Selatan",
  "district": "Mampang Prapatan",
  "zone": "Kemang",
  "postal_code": "12730"
}
```

---

## 16. Screenshot on Failure

Requirement assignment meminta screenshot failure masuk ke Allure.

Tambahkan hook Pytest, contoh:

```python
import allure
import pytest


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            screenshot = page.screenshot(full_page=True)
            allure.attach(
                screenshot,
                name="failure_screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
```

Jika kamu membuat context/page sendiri dari `browser.new_context()`, pastikan fixture/hook bisa mengakses object `page`. Alternatifnya, attach screenshot langsung di `except/finally`, tetapi jangan swallow failure.

---

## 17. Run Web Test

Run semua web tests:

```bash
pytest web/tests --alluredir=allure-results
```

Run hanya test login:

```bash
pytest web/tests/test_login.py --alluredir=allure-results
```

Run hanya create company:

```bash
pytest web/tests/test_company.py --alluredir=allure-results
```

Run headed mode untuk debugging:

```bash
HEADLESS=false pytest web/tests --alluredir=allure-results
```

Run dengan marker:

```bash
pytest -m web --alluredir=allure-results
pytest -m tier2 --alluredir=allure-results
```

---

## 18. Generate & Open Allure Report

Generate report:

```bash
allure generate allure-results -o allure-report --clean
```

Open report:

```bash
allure open allure-report
```

---

## 19. Debugging Tips

### Jalankan Playwright headed

```bash
HEADLESS=false pytest web/tests/test_company.py -s
```

### Gunakan Playwright codegen hanya untuk eksplorasi

```bash
playwright codegen https://esuite.edot.id
```

> Jangan copy mentah semua hasil codegen ke final code. Rapikan ke Page Object Model dan gunakan locator priority sesuai requirement.

### Trace Playwright

Jika ingin menambahkan trace saat debugging:

```bash
pytest web/tests --tracing=retain-on-failure
```

---

## 20. Checklist Sebelum Submit

- [ ] Web menggunakan Playwright + Pytest.
- [ ] Tidak memakai Selenium.
- [ ] Tidak memakai `time.sleep()`.
- [ ] Page Object Model diterapkan.
- [ ] Raw selector tidak berada di test file.
- [ ] Login dilakukan sekali per session menggunakan `storage_state`.
- [ ] Test login assert `Welcome Back,`.
- [ ] Create company menggunakan AI-generated data atau deterministic fallback.
- [ ] Verify detail menggunakan Tier 2 assertion field by field.
- [ ] Company yang dibuat dihapus di akhir run.
- [ ] Screenshot failure masuk ke Allure.
- [ ] Data test yang digunakan ter-attach ke Allure.
- [ ] Tidak ada credential/API key yang di-commit.
- [ ] README dan AI_USAGE.md sudah menjelaskan cara run dan penggunaan AI.

---

## 21. Recommended Run Order

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
playwright install

# 3. Export env vars if not using .env
export ESUITE_BASE_URL="https://esuite.edot.id"
export ESUITE_EMAIL="it.qa@edot.id"
export ESUITE_PASSWORD="it.QA2025"
export HEADLESS="false"

# 4. Run web suite
pytest web/tests --alluredir=allure-results

# 5. Generate Allure report
allure generate allure-results -o allure-report --clean

# 6. Open Allure report
allure open allure-report
```

---

## 22. Notes for Reviewer

- The web suite verifies behavior using Tier 2 assertions for data creation.
- A success toast is not considered enough for create company.
- The suite attempts to clean up created company data after each run.
- AI is used for test data generation, but never to weaken assertions, skip failures, or change expected values.
