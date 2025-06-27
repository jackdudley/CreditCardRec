from pydantic import BaseModel, EmailStr
from Enums import SpendingCatagory, CreditScoreRating
from datetime import datetime

class User(BaseModel):
    name: str
    email: EmailStr
    spending_catagories: list[SpendingCatagory]
    credit_score: list[CreditScoreRating]
    annual_income: int
    created_at: datetime
