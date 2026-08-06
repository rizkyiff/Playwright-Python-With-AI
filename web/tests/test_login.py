# Import modul os untuk membaca environment variable
import os
# Import pytest sebagai test framework
import pytest
# Import expect dari Playwright untuk assertion
from playwright.sync_api import expect
# Import DashboardPage untuk verifikasi halaman dashboard
from web.pages.dashboard_page import DashboardPage


# Decorator: tandai test ini sebagai kategori "web" (bisa difilter via -m web)
@pytest.mark.web
# Decorator: tandai test ini sebagai "tier1" — verifikasi navigasi dasar & display
@pytest.mark.tier1
# Definisi test function — parameter 'browser' dan 'logged_in_state' adalah Pytest fixtures
# 'browser' = instance browser Playwright (dari pytest-playwright)
# 'logged_in_state' = path ke file .web_auth/state.json (dari conftest.py)
def test_login_success(browser, logged_in_state):
    """
    Test login scenario:
    - Reuses session storage state
    - Navigates to eSuite
    - Asserts dashboard greeting 'Welcome Back,' is displayed
    """
    # Buat browser context baru dengan storage_state dari file cache login
    # storage_state = load cookies + localStorage dari state.json → browser langsung "logged in"
    context = browser.new_context(storage_state=logged_in_state)
    page = context.new_page()  # Buka tab/halaman baru di browser context

    # Navigasi ke base URL eSuite (dari env variable, default: https://esuite.edot.id)
    page.goto(os.getenv("ESUITE_BASE_URL", "https://esuite.edot.id"))

    # Buat instance DashboardPage dan verifikasi dashboard loaded
    dashboard_page = DashboardPage(page)
    dashboard_page.assert_loaded()  # Assert "Welcome Back," visible → test PASS jika muncul

    context.close()  # Tutup browser context setelah test selesai (cleanup resources)
