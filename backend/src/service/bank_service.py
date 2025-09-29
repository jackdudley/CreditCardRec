from typing import Optional, List
from src.model.card import Bank
from src.repository.bank_repository import BankRepository


class BankService:

    def __init__(self, bank_repo: BankRepository):
        self.bank_repo = bank_repo

    def create_bank(self, bank: Bank) -> Bank:
        return self.bank_repo.create_bank(bank)

    def get_bank_by_id(self, bank_id: int) -> Optional[Bank]:
        return self.bank_repo.get_bank_by_id(bank_id)

    def get_all_banks(self, limit: Optional[int] = None, offset: int = 0) -> List[Bank]:
        return self.bank_repo.get_all_banks(limit=limit, offset=offset)

    def get_relationship_banks(self) -> List[Bank]:
        return self.bank_repo.get_relationship_banks()

    def get_banks_that_report_under_eighteen(self) -> List[Bank]:
        return self.bank_repo.get_banks_that_report_under_eighteen()

    def get_banks_with_transfer_points(self) -> List[Bank]:
        return self.bank_repo.get_banks_with_transfer_points()

    def bank_exists(self, bank_id: int) -> bool:
        return self.bank_repo.bank_exists(bank_id)

    def get_bank_by_name(self, name: str) -> Optional[Bank]:
        return self.bank_repo.get_bank_by_name(name)

    def update_bank(self, bank: Bank) -> Optional[Bank]:
        return self.bank_repo.update_bank(bank)

    def delete_bank(self, bank_id: int) -> bool:
        return self.bank_repo.delete_bank(bank_id)
