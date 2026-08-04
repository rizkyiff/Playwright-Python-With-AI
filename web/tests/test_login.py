import os
import pytest
from playwright.sync_api import expect
from web.pages.dashboard_page import DashboardPage


@pytest.mark.web
@pytest.mark.tier1
def test_login_success(browser, logged_in_state):
    """
    Test login scenario:
    - Reuses session storage state
    - Navigates to eSuite
    - Asserts dashboard greeting 'Welcome Back,' is displayed
    """
    context = browser.new_context(storage_state=logged_in_state)
    page = context.new_page()
    page.goto(os.getenv("ESUITE_BASE_URL", "https://esuite.edot.id"))

    dashboard_page = DashboardPage(page)
    dashboard_page.assert_loaded()

    context.close()
