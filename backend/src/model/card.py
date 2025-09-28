from .enums import RewardStructure, SpendingCategory, CardType
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from typing import List

class CardSpendingCategory(BaseModel):
    id: Optional[int] = None
    category: SpendingCategory
    rate: float
    cap: Optional[float] = None
    quarterly_rotating: bool = False
    def __eq__(self, other):
        if(other.isinstance(CardSpendingCategory)):
            return self.category == other.category and self.rate == other.rate
        return False

class UserSpendingCategory(BaseModel):
    id: Optional[int] = None
    category: SpendingCategory
    user_spend: int

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
    annual_fee: int = 0
    foreign_transaction_fee: Optional[float] = 0
    reward_structure: RewardStructure
    spending_categories: List[CardSpendingCategory]
    created_at: Optional[datetime] = None
