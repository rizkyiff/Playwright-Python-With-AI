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
    company_data = get_company_data()

    # Requirement: Attach used test data to Allure
    allure.attach(
        str(company_data),
        name="Company test data used",
        attachment_type=allure.attachment_type.TEXT,
    )

    context = browser.new_context(storage_state=logged_in_state)
    page = context.new_page()
    page.goto(os.getenv("ESUITE_BASE_URL", "https://esuite.edot.id"))

    # Assert Dashboard load
    dashboard_page = DashboardPage(page)
    dashboard_page.assert_loaded()

    # Navigate to Companies
    companies_page = CompaniesPage(page)
    companies_page.open()
    companies_page.click_add_company()

    # Complete Form Wizard (3 Steps)
    sample_doc = "web/data/1.png"
    form_page = CompanyFormPage(page)
    form_page.complete_register_company_wizard(company_data, sample_doc_path=sample_doc)


    # Tier 2 Field-by-field verification
    detail_page = CompanyDetailPage(page)
    detail_page.assert_company_detail_matches(company_data)

    # Clean up (Mandatory cleanup step for shared env)
    form_page.delete_created_company(company_data["company_name"])

    context.close()

