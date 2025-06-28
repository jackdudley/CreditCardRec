from pydantic import BaseModel, EmailStr
from Enums import SpendingCatagory, CreditScoreRating
from typing import Optional
from datetime import datetime

class SpendingCatagoryUser():
    catagory: SpendingCatagory
    user_spend: float

class User(BaseModel):
    name: str
    email: EmailStr
    spending_catagories: list[SpendingCatagoryUser]
    authorized_user_time = Optional[int]
    credit_score: list[CreditScoreRating]
    annual_income: int
    created_at: datetime
