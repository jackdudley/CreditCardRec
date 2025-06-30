from enums import RewardStructure, SpendingCategory, CardType
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class SpendingCategoryInfo():
    id: Optional[int] = None
    card_id: int
    category: SpendingCategory
    rate: float
    cap: Optional[float] = None
    quarterly_rotating: bool = False

class Bank():
    id: Optional[int]
    name: str
    relationship_bank: bool
    transfer_points_value_cents: Optional[float] = None
    reports_under_eighteen: bool
    created_at: Optional[datetime] = None

class Card(BaseModel):
    id: Optional[int]
    name: str
    bank_id: int
    card_type: CardType
    sub_max_value: Optional[int]
    sub_description: Optional[str]
    annual_fee: int = 0
    foreign_transaction_fee: Optional[float] = None
    spending_catagories: list[SpendingCategoryInfo] = []
    reward_structure: RewardStructure
    fee_credits: Optional[str] = None
    other_benefits: Optional[str] = None
    created_at: Optional[datetime] = None
