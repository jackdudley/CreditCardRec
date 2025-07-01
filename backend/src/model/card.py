from .enums import RewardStructure, SpendingCategory, CardType
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class SpendingCategoryInfo(BaseModel):
    id: Optional[int] = None
    card_id: int
    category: SpendingCategory
    rate: float
    cap: Optional[float] = None
    quarterly_rotating: bool = False

    def __eq__(self, other):
        if(other.isistance(SpendingCategoryInfo)):
            return self.category == other.category and self.rate == other.rate
        return False

class Bank(BaseModel):
    id: Optional[int] = None
    name: str
    relationship_bank: bool
    transfer_points_value_cents: Optional[float] = None
    reports_under_eighteen: bool
    created_at: Optional[datetime] = None

class Card(BaseModel):
    id: Optional[int] = None
    name: str
    bank_id: int
    card_type: CardType
    sub_max_value: Optional[int] = None
    sub_description: Optional[str] = None
    annual_fee: int = 0
    foreign_transaction_fee: Optional[float] = 0
    reward_structure: RewardStructure
    fee_credits: Optional[str] = None
    other_benefits: Optional[str] = None
    created_at: Optional[datetime] = None
