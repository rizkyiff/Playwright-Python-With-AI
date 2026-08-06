# Import modul json untuk serialisasi/deserialisasi JSON (request body & response parsing)
import json
# Import modul logging untuk pencatatan log
import logging
# Import modul os untuk membaca environment variable (AI_API_KEY, AI_BASE_URL, AI_MODEL)
import os
# Import urllib.request untuk HTTP request ke AI API (tanpa dependency tambahan seperti requests)
import urllib.request
# Import random (tidak digunakan saat ini, tersedia untuk future use)
import random
# Import Pydantic model untuk validasi output AI
from ai.schemas import CompanyData

# Buat logger untuk modul ini
logger = logging.getLogger(__name__)


# Function: generate data perusahaan menggunakan AI Model API
def generate_ai_company_data(api_key: str) -> dict:
    """
    Generates realistic Indonesian company test data using an AI Model API,
    validating output against CompanyData Pydantic schema and printing AI logs.
    """
    # Susun prompt terstruktur yang menjelaskan schema data yang diinginkan ke AI
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

    # Log prompt yang dikirim ke AI (untuk transparansi dan debugging)
    print("\n[AI Generator] Requesting AI Model for test data generation...")
    print(f"[AI Generator] Prompt Sent:\n{prompt}")

    # Baca konfigurasi AI dari environment variable
    base_url = os.getenv("AI_BASE_URL", "https://ai.sumopod.com/v1").rstrip("/")  # Base URL API (hapus trailing /)
    ai_model = os.getenv("AI_MODEL", "gpt-4o-mini")  # Nama model AI yang digunakan

    # Susun URL endpoint untuk chat completions (format OpenAI-compatible)
    url = f"{base_url}/chat/completions"
    # Header HTTP: content-type JSON + authorization Bearer token
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",  # API key sebagai Bearer token
    }
    # Body request: model, messages (prompt), temperature, response_format
    payload = {
        "model": ai_model,  # Model yang digunakan (misal: gpt-4o-mini)
        "messages": [{"role": "user", "content": prompt}],  # Prompt sebagai user message
        "temperature": 0.7,  # Temperature 0.7 = cukup kreatif tapi terkontrol
        "response_format": {"type": "json_object"},  # Paksa output format JSON (bukan markdown)
    }

    # Buat HTTP POST request ke AI API
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    # Kirim request dengan timeout 10 detik
    with urllib.request.urlopen(req, timeout=10) as resp:
        res_data = json.loads(resp.read().decode("utf-8"))  # Parse response JSON
        raw_text = res_data["choices"][0]["message"]["content"]  # Ambil content dari response AI

    # Log raw response dari AI (untuk debugging)
    print(f"\n[AI Generator] Raw AI Model Response Received:\n{raw_text}")

    # Parse string JSON dari response AI menjadi dictionary Python
    parsed = json.loads(raw_text)

    # Post-processing: pastikan nama perusahaan tidak melebihi 30 karakter
    if "company_name" in parsed and len(parsed["company_name"]) > 30:
        parsed["company_name"] = parsed["company_name"][:30]  # Potong ke 30 char

    # Validasi data menggunakan Pydantic schema — jika tidak valid, raise ValidationError
    validated = CompanyData(**parsed)
    validated_dict = validated.model_dump()  # Konversi Pydantic model ke dictionary
    # Log schema target dan konfirmasi validasi berhasil
    print(f"\n[AI Generator] Target Pydantic Schema:\n{json.dumps(CompanyData.model_json_schema(), indent=2)}")
    print("\n[AI Generator] Schema Validation SUCCESS!")
    return validated_dict  # Return dictionary data yang sudah tervalidasi
