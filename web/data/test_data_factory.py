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


INDONESIAN_REGIONS = [
    {
        "province": "DKI JAKARTA",
        "city": "JAKARTA UTARA",
        "district": "KELAPA GADING",
        "zone": "KELAPA GADING BARAT",
        "postal_code": "14240",
    },
    {
        "province": "DKI JAKARTA",
        "city": "JAKARTA SELATAN",
        "district": "MAMPANG PRAPATAN",
        "zone": "KUNINGAN BARAT",
        "postal_code": "12710",
    },
]


def generate_deterministic_company_data() -> dict:
    """Generate realistic Indonesian business data using Faker (max 30 chars for company name)."""
    unique_suffix = random.randint(1000, 9999)
    # Ensure company_name length is max 30 characters
    company_name = f"PT QA {fake.first_name()} {unique_suffix}"[:30]
    region = random.choice(INDONESIAN_REGIONS)
    
    data = {
        "company_name": company_name,
        "email": f"qa.{unique_suffix}.{fake.free_email()}",
        "phone": f"08{random.randint(100000000, 999999999)}",
        "industry_type": "Retail",
        "company_type": "Importer/Exporter",
        "language": "Indonesia",
        "street_address": fake.street_address(),
        "country": "Indonesia",
        "province": region["province"],
        "city": region["city"],
        "district": region["district"],
        "zone": region["zone"],
        "postal_code": region["postal_code"],
        "branch_name": f"Cabang {fake.city()}"[:30],

    }
    # Validate with schema
    validated = CompanyData(**data)
    return validated.model_dump()


def get_company_data() -> dict:
    """
    Retrieves company test data. Uses AI generator if AI_API_KEY is configured,
    otherwise falls back to deterministic Faker data generation with log message.
    Logs generated data to console.
    """
    ai_api_key = os.getenv("AI_API_KEY")
    data = None

    if ai_api_key:
        print("\n[AI Data Factory] AI_API_KEY detected. Invoking AI Data Generator...")
        logger.info("[AI Data Factory] AI_API_KEY detected. Using AI test data generator.")
        try:
            from ai.generated_data import generate_ai_company_data
            data = generate_ai_company_data(ai_api_key)
        except Exception as e:
            print(f"[AI Data Factory] AI Generator encountered error/fallback: {e}")
            logger.warning(f"[AI Data Factory] Error in AI generation ({e}). Falling back to Faker.")
            print("[AI Data Factory] Using deterministic Faker data generator fallback.")
            data = generate_deterministic_company_data()
    else:
        print("\n[AI Data Factory] AI_API_KEY not configured. Falling back to deterministic Faker data generator.")
        logger.info("[AI Data Factory] AI_API_KEY not configured. Falling back to deterministic Faker data generator.")
        data = generate_deterministic_company_data()

    print("\n=================== [COMPANY TEST DATA USED] ===================")
    for key, value in data.items():
        print(f"  {key:<16}: {value}")
    print("=================================================================\n")

    return data
