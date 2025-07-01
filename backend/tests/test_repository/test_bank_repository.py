import pytest, psycopg, os
from unittest.mock import Mock, patch
from datetime import datetime
from dotenv import load_dotenv
from src.repository.bank_repository import BankRepository
from src.model.card import Bank

load_dotenv()

class TestBankRepository():

    @pytest.fixture
    def test_db_connection(self):
        """Create a test database connection"""
        conn = psycopg.connect(os.getenv("TEST_DB_URL"))
        yield conn
        conn.close()

    @pytest.fixture()
    def clean_db(self, test_db_connection):
        """Clean database before each test"""
        with test_db_connection.cursor() as cur:
            cur.execute("TRUNCATE users, banks, credit_cards, card_spending_category, authorized_user_info, user_spending_category RESTART IDENTITY CASCADE")
        test_db_connection.commit()
        yield test_db_connection

    @pytest.fixture
    def bank_repo(self):
        return BankRepository(os.getenv("TEST_DB_URL"))
    
    @pytest.fixture
    def model_bank(self):
        return Bank(
            name="Chase",
            relationship_bank=True,
            transfer_points_value_cents=1.25,
            reports_under_eighteen=False
        )

    def test_create_bank_success(self, bank_repo, clean_db, model_bank):
        """Test creating a new bank"""
        # Act
        result = bank_repo.create_bank(model_bank)
        
        # Assert
        assert result is not None
        assert isinstance(result, Bank)
        assert result.id is not None
        assert isinstance(result.id, int)
        assert result.id > 0
        
        assert result.name == model_bank.name
        assert result.relationship_bank == model_bank.relationship_bank
        assert result.transfer_points_value_cents == model_bank.transfer_points_value_cents
        assert result.reports_under_eighteen == model_bank.reports_under_eighteen
        
        assert result.created_at is not None
        assert isinstance(result.created_at, datetime)
        
        assert model_bank.id == result.id
        assert model_bank.created_at == result.created_at
        assert result is model_bank

    def test_get_bank_by_id_success(self, bank_repo, clean_db, model_bank):
        """Test successfully retrieving a bank by ID"""
        # Arrange
        created_bank = bank_repo.create_bank(model_bank)
        
        # Act
        result = bank_repo.get_bank_by_id(created_bank.id)
        
        # Assert
        assert result is not None
        assert isinstance(result, Bank)
        assert result.id == created_bank.id
        assert result.name == created_bank.name
        assert result.relationship_bank == created_bank.relationship_bank
        assert result.transfer_points_value_cents == created_bank.transfer_points_value_cents
        assert result.reports_under_eighteen == created_bank.reports_under_eighteen
        assert result.created_at == created_bank.created_at

    def test_get_bank_by_id_not_found(self, bank_repo, clean_db):
        """Test retrieving a bank that doesn't exist"""
        # Arrange
        non_existent_id = 99999
        
        # Act
        result = bank_repo.get_bank_by_id(non_existent_id)
        
        # Assert
        assert result is None

    def test_get_bank_by_id_with_none_values(self, bank_repo, clean_db):
        """Test retrieving a bank with optional None values"""
        # Arrange
        minimal_bank = Bank(
            name="Basic Bank",
            relationship_bank=False,
            transfer_points_value_cents=None,
            reports_under_eighteen=True
        )
        created_bank = bank_repo.create_bank(minimal_bank)
        
        # Act
        result = bank_repo.get_bank_by_id(created_bank.id)
        
        # Assert
        assert result is not None
        assert result.id == created_bank.id
        assert result.name == "Basic Bank"
        assert result.relationship_bank is False
        assert result.transfer_points_value_cents is None
        assert result.reports_under_eighteen is True

    def test_update_bank_success(self, bank_repo, clean_db, model_bank):
        """Test successfully updating a bank"""
        # Arrange
        created_bank = bank_repo.create_bank(model_bank)
        
        # Modify the bank
        created_bank.name = "Updated Bank Name"
        created_bank.relationship_bank = False
        created_bank.transfer_points_value_cents = 2.0
        
        # Act
        result = bank_repo.update_bank(created_bank)
        
        # Assert
        assert result is not None
        assert isinstance(result, Bank)
        assert result.id == created_bank.id
        assert result.name == "Updated Bank Name"
        assert result.relationship_bank is False
        assert result.transfer_points_value_cents == 2.0
        assert result.created_at == created_bank.created_at
        assert result is created_bank

    def test_update_bank_not_found(self, bank_repo, clean_db):
        """Test updating a bank that doesn't exist"""
        # Arrange
        non_existent_bank = Bank(
            id=99999,
            name="Non-existent Bank",
            relationship_bank=True,
            reports_under_eighteen=False
        )
        
        # Act
        result = bank_repo.update_bank(non_existent_bank)
        
        # Assert
        assert result is None

    def test_delete_bank_success(self, bank_repo, clean_db, model_bank):
        """Test successfully deleting a bank"""
        # Arrange
        created_bank = bank_repo.create_bank(model_bank)
        
        # Act
        result = bank_repo.delete_bank(created_bank.id)
        
        # Assert
        assert result is True
        
        # Verify bank is deleted
        deleted_bank = bank_repo.get_bank_by_id(created_bank.id)
        assert deleted_bank is None

    def test_delete_bank_not_found(self, bank_repo, clean_db):
        """Test deleting a bank that doesn't exist"""
        # Arrange
        non_existent_id = 99999
        
        # Act
        result = bank_repo.delete_bank(non_existent_id)
        
        # Assert
        assert result is False

    def test_get_all_banks_success(self, bank_repo, clean_db):
        """Test getting all banks without pagination"""
        # Arrange
        bank1 = Bank(
            name="Bank A",
            relationship_bank=True,
            reports_under_eighteen=False
        )
        bank2 = Bank(
            name="Bank B",
            relationship_bank=False,
            reports_under_eighteen=True
        )
        
        created_bank1 = bank_repo.create_bank(bank1)
        created_bank2 = bank_repo.create_bank(bank2)
        
        # Act
        result = bank_repo.get_all_banks()
        
        # Assert
        assert len(result) == 2
        assert all(isinstance(bank, Bank) for bank in result)
        # Should be ordered by name
        assert result[0].name == "Bank A"
        assert result[1].name == "Bank B"

    def test_get_all_banks_with_limit(self, bank_repo, clean_db):
        """Test getting all banks with limit"""
        # Arrange
        for i in range(5):
            bank = Bank(
                name=f"Bank {i}",
                relationship_bank=True,
                reports_under_eighteen=False
            )
            bank_repo.create_bank(bank)
        
        # Act
        result = bank_repo.get_all_banks(limit=3)
        
        # Assert
        assert len(result) == 3

    def test_get_all_banks_with_offset(self, bank_repo, clean_db):
        """Test getting all banks with offset"""
        # Arrange
        for i in range(5):
            bank = Bank(
                name=f"Bank {i}",
                relationship_bank=True,
                reports_under_eighteen=False
            )
            bank_repo.create_bank(bank)
        
        # Act
        result = bank_repo.get_all_banks(limit=2, offset=2)
        
        # Assert
        assert len(result) == 2

    def test_get_all_banks_no_banks(self, bank_repo, clean_db):
        """Test getting all banks when none exist"""
        # Act
        result = bank_repo.get_all_banks()
        
        # Assert
        assert result == []

    def test_get_relationship_banks_success(self, bank_repo, clean_db):
        """Test getting relationship banks"""
        # Arrange
        bank1 = Bank(
            name="Relationship Bank",
            relationship_bank=True,
            reports_under_eighteen=False
        )
        bank2 = Bank(
            name="Regular Bank",
            relationship_bank=False,
            reports_under_eighteen=False
        )
        
        bank_repo.create_bank(bank1)
        bank_repo.create_bank(bank2)
        
        # Act
        result = bank_repo.get_relationship_banks()
        
        # Assert
        assert len(result) == 1
        assert result[0].relationship_bank is True
        assert result[0].name == "Relationship Bank"

    def test_get_relationship_banks_no_banks(self, bank_repo, clean_db):
        """Test getting relationship banks when none exist"""
        # Act
        result = bank_repo.get_relationship_banks()
        
        # Assert
        assert result == []

    def test_get_banks_that_report_under_eighteen_success(self, bank_repo, clean_db):
        """Test getting banks that report under 18"""
        # Arrange
        bank1 = Bank(
            name="Reports Under 18",
            relationship_bank=True,
            reports_under_eighteen=True
        )
        bank2 = Bank(
            name="No Reporting",
            relationship_bank=False,
            reports_under_eighteen=False
        )
        
        bank_repo.create_bank(bank1)
        bank_repo.create_bank(bank2)
        
        # Act
        result = bank_repo.get_banks_that_report_under_eighteen()
        
        # Assert
        assert len(result) == 1
        assert result[0].reports_under_eighteen is True
        assert result[0].name == "Reports Under 18"

    def test_get_banks_that_report_under_eighteen_no_banks(self, bank_repo, clean_db):
        """Test getting banks that report under 18 when none exist"""
        # Act
        result = bank_repo.get_banks_that_report_under_eighteen()
        
        # Assert
        assert result == []

    def test_get_banks_with_transfer_points_success(self, bank_repo, clean_db):
        """Test getting banks with transfer points"""
        # Arrange
        bank1 = Bank(
            name="High Value Bank",
            relationship_bank=True,
            transfer_points_value_cents=2.5,
            reports_under_eighteen=False
        )
        bank2 = Bank(
            name="Low Value Bank",
            relationship_bank=False,
            transfer_points_value_cents=1.0,
            reports_under_eighteen=False
        )
        bank3 = Bank(
            name="No Points Bank",
            relationship_bank=False,
            transfer_points_value_cents=None,
            reports_under_eighteen=False
        )
        
        bank_repo.create_bank(bank1)
        bank_repo.create_bank(bank2)
        bank_repo.create_bank(bank3)
        
        # Act
        result = bank_repo.get_banks_with_transfer_points()
        
        # Assert
        assert len(result) == 2
        # Should be ordered by transfer_points_value_cents DESC
        assert result[0].transfer_points_value_cents == 2.5
        assert result[1].transfer_points_value_cents == 1.0
        assert result[0].name == "High Value Bank"
        assert result[1].name == "Low Value Bank"

    def test_get_banks_with_transfer_points_no_banks(self, bank_repo, clean_db):
        """Test getting banks with transfer points when none exist"""
        # Act
        result = bank_repo.get_banks_with_transfer_points()
        
        # Assert
        assert result == []

    def test_bank_exists_success(self, bank_repo, clean_db, model_bank):
        """Test checking if a bank exists"""
        # Arrange
        created_bank = bank_repo.create_bank(model_bank)
        
        # Act
        result = bank_repo.bank_exists(created_bank.id)
        
        # Assert
        assert result is True

    def test_bank_exists_not_found(self, bank_repo, clean_db):
        """Test checking if a non-existent bank exists"""
        # Arrange
        non_existent_id = 99999
        
        # Act
        result = bank_repo.bank_exists(non_existent_id)
        
        # Assert
        assert result is False

    def test_get_bank_by_name_success(self, bank_repo, clean_db, model_bank):
        """Test getting a bank by name"""
        # Arrange
        created_bank = bank_repo.create_bank(model_bank)
        
        # Act
        result = bank_repo.get_bank_by_name("Chase")
        
        # Assert
        assert result is not None
        assert isinstance(result, Bank)
        assert result.id == created_bank.id
        assert result.name == "Chase"
        assert result.relationship_bank == created_bank.relationship_bank
        assert result.transfer_points_value_cents == created_bank.transfer_points_value_cents
        assert result.reports_under_eighteen == created_bank.reports_under_eighteen

    def test_get_bank_by_name_not_found(self, bank_repo, clean_db):
        """Test getting a bank by name that doesn't exist"""
        # Act
        result = bank_repo.get_bank_by_name("Non-existent Bank")
        
        # Assert
        assert result is None

    def test_get_bank_by_name_case_sensitive(self, bank_repo, clean_db, model_bank):
        """Test that get_bank_by_name is case sensitive"""
        # Arrange
        bank_repo.create_bank(model_bank)
        
        # Act
        result = bank_repo.get_bank_by_name("chase")  # lowercase
        
        # Assert
        assert result is None  # Should not find "Chase" with lowercase "chase"

    def test_create_bank_with_special_characters(self, bank_repo, clean_db):
        """Test creating bank with special characters in name"""
        # Arrange
        special_bank = Bank(
            name="Bank & Trust Co.",
            relationship_bank=True,
            reports_under_eighteen=False
        )
        
        # Act
        result = bank_repo.create_bank(special_bank)
        
        # Assert
        assert result is not None
        assert result.name == "Bank & Trust Co."

    def test_create_multiple_banks_different_values(self, bank_repo, clean_db):
        """Test creating multiple banks with different boolean combinations"""
        # Arrange
        test_cases = [
            (True, True),
            (True, False),
            (False, True),
            (False, False)
        ]
        
        created_banks = []
        for i, (relationship_bank, reports_under_eighteen) in enumerate(test_cases):
            bank = Bank(
                name=f"Test Bank {i}",
                relationship_bank=relationship_bank,
                reports_under_eighteen=reports_under_eighteen
            )
            created_banks.append(bank_repo.create_bank(bank))
        
        # Act & Assert
        for i, (relationship_bank, reports_under_eighteen) in enumerate(test_cases):
            assert created_banks[i].relationship_bank == relationship_bank
            assert created_banks[i].reports_under_eighteen == reports_under_eighteen

    def test_update_bank_all_fields(self, bank_repo, clean_db):
        """Test updating all fields of a bank"""
        # Arrange
        original_bank = Bank(
            name="Original Bank",
            relationship_bank=False,
            transfer_points_value_cents=1.0,
            reports_under_eighteen=False
        )
        created_bank = bank_repo.create_bank(original_bank)
        
        # Modify all fields
        created_bank.name = "Updated Bank"
        created_bank.relationship_bank = True
        created_bank.transfer_points_value_cents = 3.5
        created_bank.reports_under_eighteen = True
        
        # Act
        result = bank_repo.update_bank(created_bank)
        
        # Assert
        assert result is not None
        assert result.name == "Updated Bank"
        assert result.relationship_bank is True
        assert result.transfer_points_value_cents == 3.5
        assert result.reports_under_eighteen is True

    def test_get_all_banks_ordering(self, bank_repo, clean_db):
        """Test that get_all_banks returns banks ordered by name"""
        # Arrange
        bank_names = ["Zebra Bank", "Alpha Bank", "Beta Bank"]
        for name in bank_names:
            bank = Bank(
                name=name,
                relationship_bank=True,
                reports_under_eighteen=False
            )
            bank_repo.create_bank(bank)
        
        # Act
        result = bank_repo.get_all_banks()
        
        # Assert
        assert len(result) == 3
        assert result[0].name == "Alpha Bank"
        assert result[1].name == "Beta Bank"
        assert result[2].name == "Zebra Bank"