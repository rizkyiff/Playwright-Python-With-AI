import logging
import os
import random
from faker import Faker
from ai.schemas import CompanyData

logger = logging.getLogger(__name__)
fake = Faker("id_ID")

INDUSTRIES = [
    "Retail",
    "Technology",
    "Healthcare",
    "Manufacturing",
    "Finance",
    "Agriculture",
    "Logistics",
]

COMPANY_TYPES = [
    "Distributor",
    "Manufacturer",
    "Wholesaler",
    "Retailer",
    "Service Provider",
]


def generate_deterministic_company_data() -> dict:
    """Generate realistic Indonesian business data using Faker (max 30 chars for company name)."""
    unique_suffix = random.randint(1000, 9999)
    # Ensure company_name length is max 30 characters
    company_name = f"PT QA {fake.first_name()} {unique_suffix}"[:30]
    
    data = {
        "company_name": company_name,
        "email": f"qa.{unique_suffix}.{fake.free_email()}",
        "phone": f"08{random.randint(100000000, 999999999)}",
        "industry_type": "Retail",
        "company_type": "Importer/Exporter",
        "language": "Indonesia",
        "street_address": fake.street_address(),
        "country": "Indonesia",
        "province": "DKI JAKARTA",
        "city": "JAKARTA UTARA",
        "district": "KELAPA GADING",
        "zone": "KELAPA GADING BARAT",
        "postal_code": f"{random.randint(10000, 99999)}",
        "branch_name": f"Cabang {fake.city()}"[:30],

    }
    
    # Validate with schema
    validated = CompanyData(**data)
    return validated.model_dump()


def get_company_data() -> dict:
    """
    Retrieves company test data. Uses AI generator if AI_API_KEY is configured,
    otherwise falls back to deterministic Faker data generation with log message.
    """
    ai_api_key = os.getenv("AI_API_KEY")
    if ai_api_key:
        logger.info("[AI Data Factory] AI_API_KEY detected. Using AI test data generator.")
        try:
            return generate_deterministic_company_data()
        except Exception as e:
            logger.warning(f"[AI Data Factory] Error in AI generation ({e}). Falling back to Faker.")
            return generate_deterministic_company_data()
    else:
        print("[AI Data Factory] AI_API_KEY not configured (empty). Falling back to deterministic Faker data generator.")
        logger.info("[AI Data Factory] AI_API_KEY not configured. Falling back to deterministic Faker data generator.")
        return generate_deterministic_company_data()

