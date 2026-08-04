import os
from pathlib import Path
import pytest
import allure
from dotenv import load_dotenv

from web.pages.login_page import LoginPage
from web.pages.dashboard_page import DashboardPage

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
def logged_in_state(playwright, request):
    """
    Session-scoped fixture to perform login once per test session and save authentication
    state into .web_auth/state.json, satisfying single-login session requirement.
    Respects --headed command line flag when generating initial state.
    """
    AUTH_DIR.mkdir(exist_ok=True)

    if AUTH_STATE.exists():
        return str(AUTH_STATE)

    email = os.environ.get("ESUITE_EMAIL", "it.qa@edot.id")
    password = os.environ.get("ESUITE_PASSWORD", "it.QA2025")

    # Pass headed flag if user ran pytest with --headed
    is_headed = request.config.getoption("--headed", False)
    headless = False if is_headed else HEADLESS

    browser = playwright.chromium.launch(headless=headless)
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()

    login_page = LoginPage(page)
    login_page.login(email, password, BASE_URL)

    dashboard_page = DashboardPage(page)
    dashboard_page.assert_loaded()

    context.storage_state(path=str(AUTH_STATE))
    browser.close()

    return str(AUTH_STATE)



@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest hook wrapper to automatically capture PNG screenshot on failure,
    invoke AI Failure Triage diagnostic, and attach it to Allure report.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # Trigger AI Failure Triage analysis
        try:
            from ai.failure_triage import triage_failure
            exception_text = str(report.longrepr)
            diagnosis = triage_failure(exception_text)
            allure.attach(
                diagnosis,
                name="AI Failure Triage Analysis",
                attachment_type=allure.attachment_type.TEXT,
            )
        except Exception as triage_err:
            print(f"[AI Failure Triage] Error executing triage hook: {triage_err}")

        page = item.funcargs.get("page")
        if page:
            try:
                screenshot = page.screenshot(full_page=True)
                allure.attach(
                    screenshot,
                    name="failure_screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception as e:
                print(f"Failed to capture failure screenshot: {e}")
