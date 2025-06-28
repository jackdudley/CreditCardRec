from enum import Enum
from pydantic import BaseModel, EmailStr, validator

class CreditScoreRating(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    NONE = "none"

class SpendingCatagory(str, Enum):
    GAS = "gas"
    GROCERIES = "groceries"
    DINING = "dining"
    ONLINE_RETAIL = "online_retail"
    TRAVEL = "travel"
    GENERAL = "general"
    RIDESHARE = "rideshare"
    PUBLIC_TRANSIT = "public_transit"
    ENTERTAINMENT = "entertainment"

class RewardStructure(str, Enum):
    POINTS = "points"
    CASHBACK = "cashback"

class CardType(str, Enum):
    STUDENT = "student"
    SECURED = "secured"
    BUISNESS = "business"
    GENERAL = "general"

