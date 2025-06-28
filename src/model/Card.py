from Enums import RewardStructure, SpendingCatagory, CardType
from typing import Optional

class SignUpBonus():
    days_to_complete: int
    value_dollars: float

class SpendingCatagoryInfo():
    catagory: SpendingCatagory
    rate: float
    cap: Optional[float] = None
    quarterly_rotating: bool = False

class Bank():
    relationship_bank: bool
    transfer_points_value_cents: float
    reports_under_eighteen: bool

class Card():
    name: str
    bank: Bank
    card_type: CardType
    sub: Optional[SignUpBonus] = None
    annual_fee: float = 0.0
    foriegn_transaction_fee: Optional[float] = None
    spending_catagories: list[SpendingCatagoryInfo] = []
    reward_structure: RewardStructure = []
    fee_credits: Optional[str] = None
    other_benefits: Optional[str] = None
