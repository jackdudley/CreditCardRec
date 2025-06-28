from pydantic import BaseModel, EmailStr
from enums import SpendingCatagory, CreditScoreRating
from datetime import datetime
from typing import Optional

class SpendingCatagoryUser():
    id: int
    user_id: int
    catagory: SpendingCatagory
    user_spend: float

class AuthoritzedUserInfo():
    id: int
    user_id: int
    bank_id: int
    add_after_age_eighteen: bool


class User(BaseModel):
    id: str
    name: str
    email: EmailStr
    spending_catagories: SpendingCatagoryUser = []
    authorized_user_info = Optional[AuthoritzedUserInfo] = None
    credit_score: CreditScoreRating
    annual_income: int
    created_at: datetime
