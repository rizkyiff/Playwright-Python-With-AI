import json
import logging
import os
import urllib.request
import random
from ai.schemas import CompanyData

logger = logging.getLogger(__name__)

def generate_ai_company_data(api_key: str) -> dict:
    """
    Generates realistic Indonesian company test data using an AI Model API,
    validating output against CompanyData Pydantic schema and printing AI logs.
    """
    prompt = (
        "Generate a realistic Indonesian business company profile as a raw JSON object matching schema. "
        "Strict JSON format only without markdown. Fields required:\n"
        "- company_name: String, max 30 characters, must start with 'PT QA '\n"
        "- email: String, valid email address\n"
        "- phone: String, Indonesian phone starting with '08'\n"
        "- industry_type: String, 'Retail'\n"
        "- company_type: String, 'Importer/Exporter'\n"
        "- language: String, 'Indonesia'\n"
        "- street_address: String, realistic Indonesian street address\n"
        "- country: String, 'Indonesia'\n"
        "- province: String, valid Indonesian province name in UPPERCASE (e.g. 'DKI JAKARTA')\n"
        "- city: String, valid city name matching the province in UPPERCASE (e.g. 'JAKARTA UTARA')\n"
        "- district: String, valid district name matching the city in UPPERCASE (e.g. 'KELAPA GADING')\n"
        "- zone: String, valid sub-district name matching district in UPPERCASE (e.g. 'KELAPA GADING BARAT')\n"
        "- postal_code: String, 5 digit postal code\n"
        "- branch_name: String, max 30 characters, starting with 'Cabang '\n"
    )

    print("\n[AI Generator] Requesting AI Model for test data generation...")
    print(f"[AI Generator] Prompt Sent:\n{prompt}")

    base_url = os.getenv("AI_BASE_URL", "https://ai.sumopod.com/v1").rstrip("/")
    ai_model = os.getenv("AI_MODEL", "gpt-4o-mini")

    url = f"{base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": ai_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        res_data = json.loads(resp.read().decode("utf-8"))
        raw_text = res_data["choices"][0]["message"]["content"]

    print(f"\n[AI Generator] Raw AI Model Response Received:\n{raw_text}")

    parsed = json.loads(raw_text)

    # Ensure constraints
    if "company_name" in parsed and len(parsed["company_name"]) > 30:
        parsed["company_name"] = parsed["company_name"][:30]

    validated = CompanyData(**parsed)
    validated_dict = validated.model_dump()
    print(f"\n[AI Generator] Target Pydantic Schema:\n{json.dumps(CompanyData.model_json_schema(), indent=2)}")
    print("\n[AI Generator] Schema Validation SUCCESS!")
    return validated_dict
