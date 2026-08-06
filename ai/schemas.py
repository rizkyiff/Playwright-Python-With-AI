# Import Pydantic BaseModel sebagai base class untuk schema validation
# Import Field untuk menambahkan constraint (max_length, default, description)
from pydantic import BaseModel, EmailStr, Field


# Definisi schema data perusahaan — digunakan untuk validasi data dari AI generator dan Faker
# Jika data tidak sesuai schema (misal: nama >30 char), Pydantic akan raise ValidationError
class CompanyData(BaseModel):
    # Nama perusahaan — wajib diisi, max 30 karakter (constraint dari UI eSuite)
    company_name: str = Field(..., max_length=30, description="Name of the company (max 30 chars)")
    # Email kontak — wajib diisi, format email valid
    email: str = Field(..., description="Contact email address")
    # Nomor telepon — wajib diisi, format string (bukan int, karena bisa dimulai dengan 0)
    phone: str = Field(..., description="Contact phone number")
    # Tipe industri — default "Retail" (sesuai dropdown eSuite)
    industry_type: str = Field(default="Retail", description="Industry type category")
    # Tipe perusahaan — default "Importer/Exporter"
    company_type: str = Field(default="Importer/Exporter", description="Type of company entity")
    # Bahasa sistem — default "Indonesia"
    language: str = Field(default="Indonesia", description="System language")
    # Alamat jalan — wajib diisi
    street_address: str = Field(..., description="Street level address")
    # Negara — default "Indonesia"
    country: str = Field(default="Indonesia", description="Country")
    # Provinsi — wajib diisi, format UPPERCASE (sesuai dropdown eSuite: "DKI JAKARTA")
    province: str = Field(..., description="Valid Indonesian province in UPPERCASE")
    # Kota — wajib diisi, format UPPERCASE (sesuai dropdown: "JAKARTA UTARA")
    city: str = Field(..., description="Valid city in UPPERCASE")
    # Kecamatan — wajib diisi, format UPPERCASE
    district: str = Field(..., description="Valid district in UPPERCASE")
    # Kelurahan — wajib diisi, format UPPERCASE
    zone: str = Field(..., description="Valid zone / sub-district in UPPERCASE")
    # Kode pos — wajib diisi, 5 digit string
    postal_code: str = Field(..., description="5 digit postal code")
    # Nama cabang — max 30 karakter, default "Cabang Utama"
    branch_name: str = Field(default="Cabang Utama", max_length=30, description="Branch name")
