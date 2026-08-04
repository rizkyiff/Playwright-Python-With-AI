from playwright.sync_api import Page, expect
from web.pages.base_page import BasePage


class CompaniesPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.companies_menu = page.get_by_role("link", name="Companies").or_(page.get_by_text("Companies"))
        self.add_company_button = page.get_by_role("button", name="Add Company").or_(page.get_by_text("+ Add Company")).or_(page.get_by_text("Add Company"))
        self.search_input = page.locator('input[placeholder*="Search"], input[type="search"]').first

    def open(self):
        self.companies_menu.first.click()

    def click_add_company(self):
        self.add_company_button.first.wait_for(state="visible", timeout=10000)
        self.add_company_button.first.click()

    def search_company(self, company_name: str):
        if self.search_input.is_visible(timeout=3000):
            self.search_input.fill(company_name)
            self.page.keyboard.press("Enter")

    def open_company_manage(self, company_name: str):
        self.search_company(company_name)
        # Click Manage button or link for the company row
        row = self.page.locator("tr", has_text=company_name).first
        manage_btn = row.get_by_role("button", name="Manage").or_(row.get_by_text("Manage"))
        if manage_btn.is_visible(timeout=5000):
            manage_btn.click()
        else:
            # Fallback to direct company text click if table row navigation differs
            self.page.get_by_text(company_name).first.click()
