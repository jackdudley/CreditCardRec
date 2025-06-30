from pydantic import BaseModel, EmailStr
from enums import SpendingCategory, CreditScoreRating
from datetime import datetime
from typing import Optional

class SpendingCategoryUser():
    id: int
    user_id: int
    category: SpendingCategory
    user_spend: float

class AuthorizedUserInfo():
    id: int
    user_id: int
    bank_id: int
    add_after_age_eighteen: bool


class User(BaseModel):
    id: str
    name: str
    email: EmailStr
    spending_categories: SpendingCategory = []
    authorized_user_info = AuthoritzedUserInfo = []
    credit_score: CreditScoreRating
    annual_income: int
    created_at: datetime
