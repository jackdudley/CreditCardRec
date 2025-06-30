from pydantic import BaseModel, EmailStr, Field
from .enums import SpendingCategory, CreditScoreRating
from datetime import datetime
from typing import List, Optional

class SpendingCategoryUser(BaseModel):
    id: Optional[int]
    user_id: int
    category: SpendingCategory
    user_spend: float

class AuthorizedUserInfo(BaseModel):
    id: Optional[int]
    user_id: int
    bank_id: int
    add_after_age_eighteen: bool


class User(BaseModel):
    id: Optional[str]
    name: str
    email: EmailStr
    credit_score: CreditScoreRating
    annual_income: int
    created_at: Optional[datetime]
