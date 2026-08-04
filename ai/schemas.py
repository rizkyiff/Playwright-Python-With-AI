from pydantic import BaseModel, EmailStr, Field


class CompanyData(BaseModel):
    company_name: str = Field(..., max_length=30, description="Name of the company (max 30 chars)")
    email: str = Field(..., description="Contact email address")
    phone: str = Field(..., description="Contact phone number")
    industry_type: str = Field(default="Retail", description="Industry type category")
    company_type: str = Field(default="Importer/Exporter", description="Type of company entity")
    language: str = Field(default="Indonesia", description="System language")
    street_address: str = Field(..., description="Street level address")
    country: str = Field(default="Indonesia", description="Country")
    province: str = Field(..., description="Valid Indonesian province in UPPERCASE")
    city: str = Field(..., description="Valid city in UPPERCASE")
    district: str = Field(..., description="Valid district in UPPERCASE")
    zone: str = Field(..., description="Valid zone / sub-district in UPPERCASE")
    postal_code: str = Field(..., description="5 digit postal code")
    branch_name: str = Field(default="Cabang Utama", max_length=30, description="Branch name")
