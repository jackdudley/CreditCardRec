import pytest
from src.model.card import Bank
from pydantic import ValidationError
from datetime import datetime

class TestBankModel():
    def test_bank_with_optional_omitted(self):
        bank = Bank(
            name = "Chase",
            relationship_bank = True,
            reports_under_eighteen = False
        )

        assert bank.name == "Chase"
        assert bank.relationship_bank == True
        assert bank.reports_under_eighteen == False
        assert bank.created_at is None
        assert bank.id is None
    
    def test_with_all_fields(self):
        a = datetime.now()
        bank = Bank(
            id = 2,
            name = "Chase",
            relationship_bank = True,
            reports_under_eighteen = False,
            transfer_points_value_cents=3,
            created_at=a
        )

        assert bank.name == "Chase"
        assert bank.relationship_bank == True
        assert bank.reports_under_eighteen == False
        assert bank.transfer_points_value_cents == 3
        assert bank.id == 2
        assert bank.created_at == a

    def test_with_invalid_value(self):
        a = datetime.now()
        with pytest.raises(ValidationError):
            bank = Bank(
                id = 2,
                name = "Chase",
                relationship_bank = True,
                reports_under_eighteen = False,
                transfer_points_value_cents="none!",
                created_at=a
            )
    def test_with_invalid_relationship(self):
        a = datetime.now()
        with pytest.raises(ValidationError):
            bank = Bank(
                id = 2,
                name = "Chase",
                relationship_bank = "nope!",
                reports_under_eighteen = False,
                transfer_points_value_cents=3,
                created_at=a
            )
        

