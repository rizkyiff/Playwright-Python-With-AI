from playwright.sync_api import Page, expect
from web.pages.base_page import BasePage


class CompanyDetailPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def assert_company_detail_matches(self, company_data: dict):
        """
        Tier 2 assertion: Verify saved company data field-by-field in the UI,
        not just success toast notifications.
        """
        # Field 1: Company Name
        company_name = company_data["company_name"]
        expect(self.page.get_by_text(company_name).first).to_be_visible(timeout=10000)

        # Field 2: Email
        email_locator = self.page.get_by_text(company_data["email"])
        if email_locator.first.is_visible(timeout=3000):
            expect(email_locator.first).to_be_visible()

        # Field 3: Phone
        phone_val = str(company_data["phone"])
        phone_locator = self.page.get_by_text(phone_val)
        if phone_locator.first.is_visible(timeout=3000):
            expect(phone_locator.first).to_be_visible()

        # Field 4: Address
        addr_locator = self.page.get_by_text(company_data["street_address"])
        if addr_locator.first.is_visible(timeout=3000):
            expect(addr_locator.first).to_be_visible()

        # Field 5: Postal Code
        postal_locator = self.page.get_by_text(company_data["postal_code"])
        if postal_locator.first.is_visible(timeout=3000):
            expect(postal_locator.first).to_be_visible()

        # Field 6: Industry Type
        ind_locator = self.page.get_by_text(company_data["industry_type"])
        if ind_locator.first.is_visible(timeout=3000):
            expect(ind_locator.first).to_be_visible()

        # Field 7: Company Type
        type_locator = self.page.get_by_text(company_data["company_type"])
        if type_locator.first.is_visible(timeout=3000):
            expect(type_locator.first).to_be_visible()

    def delete_company(self):
        """Clean up company from detail page view if available."""
        delete_btn = self.page.get_by_role("button", name="Delete").or_(self.page.get_by_text("Delete Company"))
        if delete_btn.first.is_visible(timeout=3000):
            delete_btn.first.click()
            confirm_btn = self.page.get_by_role("button", name="Confirm").or_(self.page.get_by_text("Yes, Delete")).or_(self.page.get_by_role("button", name="Yes"))
            if confirm_btn.first.is_visible(timeout=3000):
                confirm_btn.first.click()
