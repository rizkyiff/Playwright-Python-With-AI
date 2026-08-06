# Import modul os untuk membaca environment variable (.env)
import os
# Import Path untuk operasi path file system (cek keberadaan file, buat folder)
from pathlib import Path
# Import pytest sebagai framework testing
import pytest
# Import allure untuk attach screenshot/teks ke Allure report
import allure
# Import dotenv untuk memuat file .env ke environment variable
from dotenv import load_dotenv
# Import FileLock untuk mengunci file saat parallel execution (mencegah race condition)
from filelock import FileLock

# Import Page Object classes yang digunakan di fixture login
from web.pages.login_page import LoginPage  # Untuk melakukan login 2-step
from web.pages.dashboard_page import DashboardPage  # Untuk verifikasi login berhasil

# Muat semua variabel dari file .env ke os.environ
load_dotenv()

# Baca konfigurasi dari environment variable
BASE_URL = os.getenv("ESUITE_BASE_URL", "https://esuite.edot.id")  # URL target eSuite
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"  # Mode headless (true/false → boolean)
AUTH_DIR = Path(".web_auth")  # Path folder penyimpanan auth state
AUTH_STATE = AUTH_DIR / "state.json"  # Path file state.json (cookies + localStorage)


# Fixture: konfigurasi browser context — scope session (1x per seluruh sesi test)
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    # Override default browser_context_args dari pytest-playwright
    return {
        **browser_context_args,  # Spread existing args (preserve defaults)
        "viewport": {"width": 1440, "height": 900},  # Set viewport ke resolusi desktop standar
    }


# Fixture: return path file auth state — untuk digunakan test lain jika perlu
@pytest.fixture(scope="session")
def auth_state_path():
    return str(AUTH_STATE)  # Return path sebagai string: ".web_auth/state.json"


# Fixture UTAMA: mengelola login sekali per session dan menyimpan auth state ke file
@pytest.fixture(scope="session")
def logged_in_state(playwright, request, tmp_path_factory):
    """
    Session-scoped fixture to perform login once per test session and save authentication
    state into .web_auth/state.json, satisfying single-login session requirement.
    Uses FileLock to prevent race conditions when running with pytest-xdist parallel workers.
    Respects --headed command line flag when generating initial state.
    """
    AUTH_DIR.mkdir(exist_ok=True)  # Buat folder .web_auth/ jika belum ada (exist_ok = no error jika sudah ada)

    # === FILELOCK UNTUK PARALLEL SAFETY ===
    # Buat file lock di temp directory pytest (shared antar xdist workers)
    # tmp_path_factory.getbasetemp().parent = folder temp root (bukan per-worker)
    lock_path = tmp_path_factory.getbasetemp().parent / "auth.lock"
    with FileLock(str(lock_path)):  # Acquire lock — hanya 1 worker bisa masuk blok ini sekaligus
        # CEK CACHE: Jika state.json sudah ada, langsung return (SKIP LOGIN)
        if AUTH_STATE.exists():
            return str(AUTH_STATE)  # Pakai cache → tidak perlu login ulang

        # === FULL LOGIN FLOW (hanya jika state.json belum ada) ===

        # Baca credential dari environment variable (atau gunakan default)
        email = os.environ.get("ESUITE_EMAIL", "it.qa@edot.id")
        password = os.environ.get("ESUITE_PASSWORD", "it.QA2025")

        # Cek apakah user menjalankan pytest dengan flag --headed (untuk debugging visual)
        is_headed = request.config.getoption("--headed", False)
        headless = False if is_headed else HEADLESS  # Jika --headed → force non-headless

        # Launch browser Chromium (headless atau headed sesuai konfigurasi)
        browser = playwright.chromium.launch(headless=headless)
        # Buat browser context baru dengan viewport 1440x900
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()  # Buka tab baru

        # Jalankan login 2-step menggunakan LoginPage
        login_page = LoginPage(page)
        login_page.login(email, password, BASE_URL)  # Email → Log In → Password → Log In

        # Verifikasi login berhasil — cek "Welcome Back," di dashboard
        dashboard_page = DashboardPage(page)
        dashboard_page.assert_loaded()  # Jika gagal → fixture error, semua test skip

        # SIMPAN AUTH STATE ke file — cookies, localStorage, sessionStorage → state.json
        context.storage_state(path=str(AUTH_STATE))
        browser.close()  # Tutup browser setelah state tersimpan

    return str(AUTH_STATE)  # Return path ke file state.json untuk digunakan test



# Hook Pytest: dipanggil OTOMATIS setelah setiap test case selesai dijalankan
@pytest.hookimpl(hookwrapper=True)  # hookwrapper = bisa intercept sebelum & sesudah
def pytest_runtest_makereport(item, call):
    """
    Pytest hook wrapper to automatically capture PNG screenshot on failure,
    invoke AI Failure Triage diagnostic, and attach it to Allure report.
    """
    outcome = yield  # Yield = tunggu test selesai, lalu ambil hasilnya
    report = outcome.get_result()  # Ambil report object dari hasil test

    # Hanya proses saat phase "call" (eksekusi test body) DAN test FAILED
    if report.when == "call" and report.failed:
        # === AI FAILURE TRIAGE ===
        try:
            from ai.failure_triage import triage_failure  # Lazy import modul AI triage
            exception_text = str(report.longrepr)  # Ambil full traceback sebagai string
            diagnosis = triage_failure(exception_text)  # Analisis traceback (AI atau heuristic)
            # Attach hasil analisis ke Allure report sebagai text attachment
            allure.attach(
                diagnosis,  # Isi: root cause + fix recommendation
                name="AI Failure Triage Analysis",  # Nama attachment di Allure
                attachment_type=allure.attachment_type.TEXT,  # Tipe: plain text
            )
        except Exception as triage_err:
            # Jika triage error (import gagal, dll) → log ke console, JANGAN crash test
            print(f"[AI Failure Triage] Error executing triage hook: {triage_err}")

        # === SCREENSHOT ON FAILURE ===
        page = item.funcargs.get("page")  # Ambil instance 'page' dari test function arguments
        if page:  # Jika test menggunakan fixture 'page'
            try:
                screenshot = page.screenshot(full_page=True)  # Capture screenshot FULL PAGE (PNG)
                # Attach screenshot ke Allure report
                allure.attach(
                    screenshot,  # Data binary PNG
                    name="failure_screenshot",  # Nama attachment di Allure
                    attachment_type=allure.attachment_type.PNG,  # Tipe: image PNG
                )
            except Exception as e:
                # Jika screenshot gagal (browser sudah closed, dll) → log ke console
                print(f"Failed to capture failure screenshot: {e}")
