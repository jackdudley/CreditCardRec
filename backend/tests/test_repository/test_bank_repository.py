import pytest
from dotenv import load_dotenv
import os 
from src.repository.bank_repository import BankRepository
from src.model.card import Bank
from datetime import datetime


load_dotenv()


class TestBankRepository():
    @pytest.fixture
    def bank_repo(self):
        return BankRepository(os.getenv("TEST_DB_URL"))
    
    @pytest.fixture
    def model_bank(self):
        return Bank(
            name="Chase",
            relationship_bank=True,
            reports_under_eighteen=False
        )
    

    
    def test_add_bank(self, bank_repo, model_bank):
        """Test creating a new bank"""
        # Act
        result = bank_repo.create_bank(model_bank)
        
        # Assert
        assert result is not None
        assert isinstance(result, Bank)
        assert result.id is not None
        assert result.name == "Chase"
        assert result.relationship_bank is True
        assert result.reports_under_eighteen is False
        assert result.created_at is not None
        assert isinstance(result.created_at, datetime)