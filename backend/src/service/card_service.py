from typing import Optional, List
from src.model.card import Card, CardType, RewardStructure, CardSpendingCategory
from src.repository.card_repository import CardRepository

class CardService:

    def __init__(self, card_repo: CardRepository):
        self.card_repo = card_repo

    def create_card(self, card: Card) -> Card:
        return self.card_repo.create_card(card)

    def get_card_by_id(self, card_id: int) -> Optional[Card]:
        return self.card_repo.get_card_by_id(card_id)

    def get_all_cards(self, limit: Optional[int] = None, offset: int = 0) -> List[Card]:
        return self.card_repo.get_all_cards(limit=limit, offset=offset)

    def get_cards_by_bank(self, bank_id: int) -> List[Card]:
        return self.card_repo.get_cards_by_bank(bank_id)

    def update_card(self, card: Card) -> Optional[Card]:
        return self.card_repo.update_card(card)

    def delete_card(self, card_id: int) -> bool:
        return self.card_repo.delete_card(card_id)
