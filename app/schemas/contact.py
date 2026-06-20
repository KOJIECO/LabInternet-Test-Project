import re
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, Dict, List

PHONE_REGEX = re.compile(r"^\+?[0-9\-\s\(\)]{7,20}$")

class ContactCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr = Field(...)
    phone: str = Field(...)
    message: str = Field(..., min_length=5, max_length=5000)

    @field_validator("phone")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        cleaned = re.sub(r"[\s\-\(\)]", "", v)
        if not re.match(r"^\+?[0-9]{7,15}$", cleaned):
            raise ValueError("Некорректный формат телефона. Должно быть от 7 до 15 цифр.")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Имя не может состоять только из пробелов.")
        return v.strip()

class ContactResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    message: str
    sentiment: Optional[str]
    category: Optional[str]
    ai_response: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HealthResponse(BaseModel):
    status: str
    database: str
    ai_service: str

class MetricsResponse(BaseModel):
    total_messages: int
    sentiment_distribution: Dict[str, int]
    category_distribution: Dict[str, int]
    recent_messages: List[ContactResponse]
