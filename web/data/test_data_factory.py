# Import modul logging untuk pencatatan log ke console/file
import logging
# Import modul os untuk membaca environment variable (AI_API_KEY)
import os
# Import modul random untuk angka acak (suffix nama, pilih region)
import random
# Import Faker untuk generate data Indonesia realistis
from faker import Faker
# Import Pydantic model untuk validasi data sebelum digunakan di test
from ai.schemas import CompanyData

# Buat logger untuk modul ini (nama logger = nama file)
logger = logging.getLogger(__name__)
# Inisialisasi Faker dengan locale Indonesia — menghasilkan nama, alamat, email Indonesia
fake = Faker("id_ID")

# Daftar tipe industri yang tersedia (digunakan untuk variasi data)
INDUSTRIES = [
    "Retail",
    "Technology",
    "Healthcare",
    "Manufacturing",
    "Finance",
    "Agriculture",
    "Logistics",
]

# Daftar tipe perusahaan yang tersedia
COMPANY_TYPES = [
    "Distributor",
    "Manufacturer",
    "Wholesaler",
    "Retailer",
    "Service Provider",
]


# Pool wilayah Indonesia yang valid dan berpasangan (province → city → district → zone → postal_code)
# Data ini harus konsisten karena eSuite menggunakan cascading dropdown
INDONESIAN_REGIONS = [
    {
        "province": "DKI JAKARTA",          # Provinsi
        "city": "JAKARTA UTARA",            # Kota (child dari DKI JAKARTA)
        "district": "KELAPA GADING",        # Kecamatan (child dari JAKARTA UTARA)
        "zone": "KELAPA GADING BARAT",      # Kelurahan (child dari KELAPA GADING)
        "postal_code": "14240",             # Kode pos yang sesuai dengan kelurahan
    },
    {
        "province": "DKI JAKARTA",
        "city": "JAKARTA SELATAN",
        "district": "MAMPANG PRAPATAN",
        "zone": "KUNINGAN BARAT",
        "postal_code": "12710",
    },
]


# Function: generate data perusahaan deterministik menggunakan Faker (tanpa AI)
def generate_deterministic_company_data() -> dict:
    """Generate realistic Indonesian business data using Faker (max 30 chars for company name)."""
    unique_suffix = random.randint(1000, 9999)  # Angka acak 4 digit untuk keunikan nama
    # Buat nama perusahaan: "PT QA {nama_depan} {suffix}" — potong max 30 karakter
    company_name = f"PT QA {fake.first_name()} {unique_suffix}"[:30]
    region = random.choice(INDONESIAN_REGIONS)  # Pilih acak 1 set wilayah dari pool

    # Susun dictionary data perusahaan lengkap
    data = {
        "company_name": company_name,                          # Nama perusahaan (max 30 char)
        "email": f"qa.{unique_suffix}.{fake.free_email()}",   # Email unik: qa.1234.xxx@gmail.com
        "phone": f"08{random.randint(100000000, 999999999)}", # Telepon Indonesia: 08xxxxxxxxx
        "industry_type": "Retail",                             # Tipe industri (fixed: Retail)
        "company_type": "Importer/Exporter",                   # Tipe perusahaan (fixed)
        "language": "Indonesia",                               # Bahasa sistem
        "street_address": fake.street_address(),               # Alamat jalan acak dari Faker Indonesia
        "country": "Indonesia",                                # Negara
        "province": region["province"],                        # Provinsi dari pool wilayah
        "city": region["city"],                                # Kota (sesuai provinsi)
        "district": region["district"],                        # Kecamatan (sesuai kota)
        "zone": region["zone"],                                # Kelurahan (sesuai kecamatan)
        "postal_code": region["postal_code"],                  # Kode pos (sesuai kelurahan)
        "branch_name": f"Cabang {fake.city()}"[:30],          # Nama cabang (max 30 char)

    }
    # Validasi data menggunakan Pydantic model — jika ada field tidak valid, raise error
    validated = CompanyData(**data)
    return validated.model_dump()  # Return sebagai dict yang sudah tervalidasi


# Function utama (entry point): ambil data perusahaan — AI atau Faker
def get_company_data() -> dict:
    """
    Retrieves company test data. Uses AI generator if AI_API_KEY is configured,
    otherwise falls back to deterministic Faker data generation with log message.
    Logs generated data to console.
    """
    ai_api_key = os.getenv("AI_API_KEY")  # Baca API key dari environment variable
    data = None  # Inisialisasi variabel data

    if ai_api_key:  # Jika AI_API_KEY ada (tidak kosong)
        print("\n[AI Data Factory] AI_API_KEY detected. Invoking AI Data Generator...")
        logger.info("[AI Data Factory] AI_API_KEY detected. Using AI test data generator.")
        try:
            # Import modul AI generator (lazy import — hanya saat dibutuhkan)
            from ai.generated_data import generate_ai_company_data
            data = generate_ai_company_data(ai_api_key)  # Panggil AI API untuk generate data
        except Exception as e:
            # Jika AI error (API down, timeout, parsing error) → fallback ke Faker
            print(f"[AI Data Factory] AI Generator encountered error/fallback: {e}")
            logger.warning(f"[AI Data Factory] Error in AI generation ({e}). Falling back to Faker.")
            print("[AI Data Factory] Using deterministic Faker data generator fallback.")
            data = generate_deterministic_company_data()  # Gunakan Faker sebagai fallback
    else:  # Jika AI_API_KEY tidak ada atau kosong
        print("\n[AI Data Factory] AI_API_KEY not configured. Falling back to deterministic Faker data generator.")
        logger.info("[AI Data Factory] AI_API_KEY not configured. Falling back to deterministic Faker data generator.")
        data = generate_deterministic_company_data()  # Langsung pakai Faker

    # Print data yang digunakan ke console (untuk debugging dan transparansi)
    print("\n=================== [COMPANY TEST DATA USED] ===================")
    for key, value in data.items():  # Loop setiap field data
        print(f"  {key:<16}: {value}")  # Format: nama_field (16 char width) : nilai
    print("=================================================================\n")

    return data  # Return data yang akan digunakan oleh test
