from pydantic import BaseModel, EmailStr, Field
from .enums import SpendingCategory, CreditScoreRating
from datetime import datetime
from typing import List, Optional

class SpendingCategoryUser(BaseModel):
    id: Optional[int] = None
    user_id: int
    category: SpendingCategory
    user_spend: float
    created_at: Optional[datetime] = None

    def __eq__(self, other):
        return self.id == other.id and self.user_id == other.user_id and self.created_at == other.created_at

class AuthorizedUserInfo(BaseModel):
    id: Optional[int] = None
    user_id: int
    bank_id: int
    add_after_age_eighteen: bool
    created_at: Optional[datetime] = None


class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: EmailStr
    credit_score: CreditScoreRating
    annual_income: int
    created_at: Optional[datetime] = None

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name
