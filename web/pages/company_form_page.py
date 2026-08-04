import re
from pathlib import Path
from playwright.sync_api import Page, expect
from web.pages.base_page import BasePage

BASE_URL = "https://esuite.edot.id"


class CompanyFormPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def complete_register_company_wizard(self, data: dict, sample_doc_path: str = None):
        page = self.page

        # Step 1: Basic Info & Location
        # Using XPath by placeholder — more stable if role-based locator doesn't resolve
        # press_sequentially() simulates real keyboard input char-by-char (triggers input events)
        company_name_input = page.locator("//input[@placeholder='Input Company Name']")
        company_name_input.wait_for(state="visible", timeout=15000)
        company_name_input.click()
        company_name_input.press_sequentially(data["company_name"], delay=50)

        page.get_by_role("textbox", name="Input Email").click()
        page.get_by_role("textbox", name="Input Email").fill(data["email"])

        raw_phone = str(data["phone"])
        # Strip leading 0 — field uses country code prefix (+62)
        phone_val = raw_phone.lstrip("0") if raw_phone.startswith("0") else raw_phone
        page.get_by_role("textbox", name="Input Phone").click()
        page.get_by_role("textbox", name="Input Phone").fill(phone_val)

        page.get_by_role("combobox").filter(has_text="Choose Industry Type").click()
        page.get_by_role("option", name=data.get("industry_type", "Retail")).click()

        page.get_by_role("combobox").filter(has_text="Choose Company Type").click()
        page.get_by_role("option", name=data.get("company_type", "Importer/Exporter")).click()

        page.get_by_role("combobox").filter(has_text="Choose Language").click()
        page.get_by_role("option", name=data.get("language", "Indonesia")).click()

        page.get_by_role("textbox", name="Input Address").click()
        page.get_by_role("textbox", name="Input Address").fill(data["street_address"])

        page.get_by_role("combobox").filter(has_text="Choose Country").click()
        page.get_by_role("option", name=data.get("country", "Indonesia")).click()

        page.get_by_role("combobox").filter(has_text="Choose Province").click()
        prov_search = data.get("province", "DKI JAKARTA")[:4].lower()
        page.get_by_role("textbox", name="Search").fill(prov_search)
        page.get_by_role("option", name=data.get("province", "DKI JAKARTA")).click()

        page.get_by_role("combobox").filter(has_text="Choose City").click()
        page.get_by_role("option", name=data.get("city", "JAKARTA UTARA")).click()

        page.get_by_role("combobox").filter(has_text="Choose District").click()
        page.get_by_role("option", name=data.get("district", "KELAPA GADING")).click()

        page.get_by_role("combobox").filter(has_text="Choose Sub District").click()
        page.get_by_role("option", name=data.get("zone", "KELAPA GADING BARAT")).click()

        page.get_by_role("button", name="Next").click()

        # Step 2: Upload Legal Document
        # Button should always be present on this step — wait then click directly
        add_doc_btn = page.get_by_role("button", name="+ Add Document")
        add_doc_btn.wait_for(state="visible", timeout=10000)
        add_doc_btn.click()

        page.locator("button").filter(has_text="Choose Legal Document").click()
        page.get_by_role("option", name="Identification Card").click()

        doc_file = (
            sample_doc_path
            if sample_doc_path and Path(sample_doc_path).exists()
            else "web/data/1.png"
        )
        # Target actual file input element (input[type='file']) instead of modal label/div
        file_input = page.locator("input[type='file']").first
        if file_input.count() > 0:
            file_input.set_input_files(doc_file)
        else:
            page.get_by_label("Add Legal Document").locator("input[type='file']").set_input_files(doc_file)
        page.get_by_text("Submit Document").click()

        page.get_by_role("button", name="Next").click()

        # Step 3: Legal Address & Policy Agreement
        # Validate if Input Branch Name has a value, fill if empty
        branch_input = page.locator("//*[@placeholder='Input Branch Name']")
        if branch_input.is_visible(timeout=3000):
            if not branch_input.input_value():
                branch_val = data.get("branch_name") or "Cabang Utama"
                branch_input.click()
                branch_input.fill(branch_val)

        page.get_by_role("textbox", name="Input Address").click()
        page.get_by_role("textbox", name="Input Address").fill(data["street_address"])

        # Country combobox in step 3 — use .first (no has_text filter, matches codegen output)
        page.get_by_role("combobox").first.click()
        page.get_by_role("option", name=data.get("country", "Indonesia")).click()

        page.get_by_role("combobox").filter(has_text="Choose Province").click()
        prov_search = data.get("province", "DKI JAKARTA")[:4].lower()
        page.get_by_role("textbox", name="Search").fill(prov_search)
        page.get_by_role("option", name=data.get("province", "DKI JAKARTA")).click()

        page.get_by_role("combobox").filter(has_text="Choose City").click()
        page.get_by_role("option", name=data.get("city", "JAKARTA UTARA")).click()

        page.get_by_role("combobox").filter(has_text="Choose District").click()
        page.get_by_role("option", name=data.get("district", "KELAPA GADING")).click()

        page.get_by_role("combobox").filter(has_text="Choose Sub District").click()
        page.get_by_role("option", name=data.get("zone", "KELAPA GADING BARAT")).click()

        # Select all modules repeatedly if Register button is disabled
        select_all_cb = page.locator("#select-all")
        register_btn = page.get_by_role("button", name="Register")

        for _ in range(10):
            select_all_cb.click()
            page.wait_for_timeout(500)
            if not register_btn.is_disabled():
                break

        register_btn.click()

        # Wait for automatic redirection or URL change to /companies
        try:
            page.wait_for_url("**/companies**", timeout=10000)
        except Exception:
            page.goto(f"{BASE_URL}/companies")

        page.wait_for_load_state("networkidle")

        company_name = data["company_name"]

        company_elem = page.get_by_text(re.compile(re.escape(company_name))).first
        company_elem.wait_for(state="visible", timeout=15000)
        company_elem.click()

    def delete_created_company(self, company_name: str):
        page = self.page

        # 1. Navigate to /companies if not already there
        if "/companies" not in page.url:
            page.goto(f"{BASE_URL}/companies")

        # 2. Click Manage button using exact ancestor XPath: //*[text()='<COMPANY_NAME>']/ancestor::div[2]//button[text()='Manage']
        manage_btn = page.locator(
            f"//*[text()='{company_name}']/ancestor::div[2]//button[text()='Manage']"
        ).or_(page.get_by_role("button", name="Manage")).first
        manage_btn.wait_for(state="visible", timeout=10000)
        manage_btn.click()
        page.wait_for_timeout(1500)

        # 3. Click Delete button: //button[text()='Delete'] or button containing Delete
        delete_btn = page.locator(
            f"//*[text()='{company_name}']/ancestor::div[2]//button[text()='Delete']"
        ).or_(
            page.locator("//button[text()='Delete'] | //button[contains(text(),'Delete')]")
        ).or_(
            page.get_by_role("button", name="Delete")
        ).first
        delete_btn.wait_for(state="visible", timeout=10000)
        delete_btn.click()

        # 4. Agreement checkbox: //*[text()='I understand & agree to delete']/preceding-sibling::*
        agree_cb = page.locator(
            "//*[text()='I understand & agree to delete']/preceding-sibling::*"
        ).or_(
            page.get_by_text("I understand & agree to delete")
        ).first
        if agree_cb.is_visible(timeout=5000):
            agree_cb.click()

        # 5. Click Confirm button: //button[text()='Confirm']
        confirm_btn = page.locator(
            "//button[text()='Confirm'] | //button[contains(text(),'Confirm')]"
        ).or_(
            page.get_by_role("button", name="Confirm")
        ).first
        if confirm_btn.is_visible(timeout=5000):
            confirm_btn.click()

        # 6. Post-submit validation: Check if company name is deleted and no longer visible
        page.wait_for_timeout(2000)
        page.goto(f"{BASE_URL}/companies")
        expect(page.locator(f"//*[text()='{company_name}']")).not_to_be_visible(timeout=10000)
