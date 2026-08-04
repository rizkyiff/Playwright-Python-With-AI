from pydantic import BaseModel, EmailStr, Field


class CompanyData(BaseModel):
    company_name: str = Field(..., max_length=30, description="Name of the company (max 30 chars)")
    email: str = Field(..., description="Contact email address")
    phone: str = Field(..., description="Contact phone number")
    industry_type: str = Field(..., description="Industry type category")
    company_type: str = Field(..., description="Type of company entity")
    language: str = Field(default="Indonesia", description="System language")
    street_address: str = Field(..., description="Street level address")
    country: str = Field(default="Indonesia", description="Country")
    province: str = Field(default="DKI Jakarta", description="Province")
    city: str = Field(default="Jakarta Selatan", description="City")
    district: str = Field(default="Mampang Prapatan", description="District")
    zone: str = Field(default="Kemang", description="Zone / Sub-district")
    postal_code: str = Field(..., description="Postal code")
    branch_name: str = Field(default="Cabang Utama", description="Branch name")
