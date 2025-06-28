from pydantic import BaseModel, EmailStr
from Enums import SpendingCatagory, CreditScoreRating
from datetime import datetime
from typing import Optional
from Card import Bank

class SpendingCatagoryUser():
    catagory: SpendingCatagory
    user_spend: float

class AuthoritzedUserInfo():
    bank: Bank
    after_age_eighteen: bool


class User(BaseModel):
    name: str
    email: EmailStr
    spending_catagories: list[SpendingCatagoryUser]
    authorized_user_info = Optional[AuthoritzedUserInfo] = None
    credit_score: list[CreditScoreRating]
    annual_income: int
    created_at: datetime
