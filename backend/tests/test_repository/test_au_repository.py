import pytest, psycopg, os
from datetime import datetime
from dotenv import load_dotenv
from src.repository.authorized_user_repository import AuthorizedUserRepository
from src.repository.user_repository import UserRepository
from src.repository.bank_repository import BankRepository
from src.model.user import AuthorizedUserInfo, User
from src.model.card import Bank

load_dotenv()

class TestAuthorizedUserRepository():

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
    def au_repo(self):
        return AuthorizedUserRepository(os.getenv("TEST_DB_URL"))

    @pytest.fixture
    def user_repo(self):
        return UserRepository(os.getenv("TEST_DB_URL"))

    @pytest.fixture
    def bank_repo(self):
        return BankRepository(os.getenv("TEST_DB_URL"))

    @pytest.fixture
    def db_with_user_and_bank(self, clean_db, user_repo, bank_repo):
        """Create a user and bank for testing"""
        # Create user
        user = User(
            name="Test User",
            email="test@example.com",
            credit_score='good',
            annual_income=30000
        )
        created_user = user_repo.create_user(user)
        
        # Create bank
        bank = Bank(
            name="Test Bank",
            relationship_bank=True,
            reports_under_eighteen=False
        )
        created_bank = bank_repo.create_bank(bank)
        
        return created_user, created_bank

    @pytest.fixture
    def model_au_info(self, db_with_user_and_bank):
        user, bank = db_with_user_and_bank
        return AuthorizedUserInfo(
            user_id=user.id,
            bank_id=bank.id,
            add_after_age_eighteen=True
        )

    def test_add_info_success(self, au_repo, clean_db, model_au_info):
        """Test successfully adding authorized user info"""
        # Act
        result = au_repo.add_info(model_au_info)
        
        # Assert
        assert result is not None
        assert isinstance(result, AuthorizedUserInfo)
        assert result.id is not None
        assert isinstance(result.id, int)
        assert result.id > 0
        
        assert result.user_id == model_au_info.user_id
        assert result.bank_id == model_au_info.bank_id
        assert result.add_after_age_eighteen == model_au_info.add_after_age_eighteen
        
        assert result.created_at is not None
        assert isinstance(result.created_at, datetime)
        
        assert model_au_info.id == result.id
        assert model_au_info.created_at == result.created_at
        assert result is model_au_info

    def test_get_info_by_id_success(self, au_repo, clean_db, model_au_info):
        """Test successfully retrieving authorized user info by ID"""
        # Arrange
        created_info = au_repo.add_info(model_au_info)
        
        # Act
        result = au_repo.get_info_by_id(created_info.id)
        
        # Assert
        assert result is not None
        assert isinstance(result, AuthorizedUserInfo)
        assert result.id == created_info.id
        assert result.user_id == created_info.user_id
        assert result.bank_id == created_info.bank_id
        assert result.add_after_age_eighteen == created_info.add_after_age_eighteen
        assert result.created_at == created_info.created_at

    def test_get_info_by_id_not_found(self, au_repo, clean_db):
        """Test retrieving authorized user info that doesn't exist"""
        # Arrange
        non_existent_id = 99999
        
        # Act
        result = au_repo.get_info_by_id(non_existent_id)
        
        # Assert
        assert result is None

    def test_remove_info_success(self, au_repo, clean_db, model_au_info):
        """Test successfully removing authorized user info"""
        # Arrange
        created_info = au_repo.add_info(model_au_info)
        
        # Act
        result = au_repo.remove_info(created_info.id)
        
        # Assert
        assert result is True
        
        # Verify info is deleted
        deleted_info = au_repo.get_info_by_id(created_info.id)
        assert deleted_info is None

    def test_remove_info_not_found(self, au_repo, clean_db):
        """Test removing authorized user info that doesn't exist"""
        # Arrange
        non_existent_id = 99999
        
        # Act
        result = au_repo.remove_info(non_existent_id)
        
        # Assert
        assert result is False

    def test_get_all_info_by_user_success(self, au_repo, clean_db, db_with_user_and_bank):
        """Test getting all authorized user info for a user"""
        # Arrange
        user, bank = db_with_user_and_bank
        
        info1 = AuthorizedUserInfo(
            user_id=user.id,
            bank_id=bank.id,
            add_after_age_eighteen=True
        )
        info2 = AuthorizedUserInfo(
            user_id=user.id,
            bank_id=bank.id,
            add_after_age_eighteen=False
        )
        
        created_info1 = au_repo.add_info(info1)
        created_info2 = au_repo.add_info(info2)
        
        # Act
        result = au_repo.get_all_info_by_user(user.id)
        
        # Assert
        assert len(result) == 2
        assert all(isinstance(info, AuthorizedUserInfo) for info in result)
        assert all(info.user_id == user.id for info in result)
        # Should be ordered by created_at DESC (most recent first)
        assert result[0].id == created_info2.id
        assert result[1].id == created_info1.id

    def test_get_all_info_by_user_no_info(self, au_repo, clean_db, db_with_user_and_bank):
        """Test getting all authorized user info for user with no info"""
        # Arrange
        user, bank = db_with_user_and_bank
        
        # Act
        result = au_repo.get_all_info_by_user(user.id)
        
        # Assert
        assert result == []

    def test_get_all_info_by_bank_success(self, au_repo, clean_db, db_with_user_and_bank):
        """Test getting all authorized user info for a bank"""
        # Arrange
        user, bank = db_with_user_and_bank
        
        info1 = AuthorizedUserInfo(
            user_id=user.id,
            bank_id=bank.id,
            add_after_age_eighteen=True
        )
        info2 = AuthorizedUserInfo(
            user_id=user.id,
            bank_id=bank.id,
            add_after_age_eighteen=False
        )
        
        created_info1 = au_repo.add_info(info1)
        created_info2 = au_repo.add_info(info2)
        
        # Act
        result = au_repo.get_all_info_by_bank(bank.id)
        
        # Assert
        assert len(result) == 2
        assert all(isinstance(info, AuthorizedUserInfo) for info in result)
        assert all(info.bank_id == bank.id for info in result)
        # Should be ordered by created_at DESC (most recent first)
        assert result[0].id == created_info2.id
        assert result[1].id == created_info1.id

    def test_get_all_info_by_bank_no_info(self, au_repo, clean_db, db_with_user_and_bank):
        """Test getting all authorized user info for bank with no info"""
        # Arrange
        user, bank = db_with_user_and_bank
        
        # Act
        result = au_repo.get_all_info_by_bank(bank.id)
        
        # Assert
        assert result == []

    def test_get_info_by_user_and_bank_success(self, au_repo, clean_db, model_au_info):
        """Test getting authorized user info by user and bank"""
        # Arrange
        created_info = au_repo.add_info(model_au_info)
        
        # Act
        result = au_repo.get_info_by_user_and_bank(model_au_info.user_id, model_au_info.bank_id)
        
        # Assert
        assert result is not None
        assert isinstance(result, AuthorizedUserInfo)
        assert result.id == created_info.id
        assert result.user_id == created_info.user_id
        assert result.bank_id == created_info.bank_id
        assert result.add_after_age_eighteen == created_info.add_after_age_eighteen

    def test_get_info_by_user_and_bank_not_found(self, au_repo, clean_db, db_with_user_and_bank):
        """Test getting authorized user info by user and bank that doesn't exist"""
        # Arrange
        user, bank = db_with_user_and_bank
        
        # Act
        result = au_repo.get_info_by_user_and_bank(user.id, bank.id)
        
        # Assert
        assert result is None

    def test_update_info_success(self, au_repo, clean_db, model_au_info):
        """Test successfully updating authorized user info"""
        # Arrange
        created_info = au_repo.add_info(model_au_info)
        
        # Modify the info
        created_info.add_after_age_eighteen = False
        
        # Act
        result = au_repo.update_info(created_info)
        
        # Assert
        assert result is not None
        assert isinstance(result, AuthorizedUserInfo)
        assert result.id == created_info.id
        assert result.add_after_age_eighteen is False
        assert result.created_at == created_info.created_at
        assert result is created_info

    def test_update_info_not_found(self, au_repo, clean_db, db_with_user_and_bank):
        """Test updating authorized user info that doesn't exist"""
        # Arrange
        user, bank = db_with_user_and_bank
        non_existent_info = AuthorizedUserInfo(
            id=99999,
            user_id=user.id,
            bank_id=bank.id,
            add_after_age_eighteen=True
        )
        
        # Act
        result = au_repo.update_info(non_existent_info)
        
        # Assert
        assert result is None

    def test_get_all_info_success(self, au_repo, clean_db, db_with_user_and_bank):
        """Test getting all authorized user info without pagination"""
        # Arrange
        user, bank = db_with_user_and_bank
        
        info1 = AuthorizedUserInfo(
            user_id=user.id,
            bank_id=bank.id,
            add_after_age_eighteen=True
        )
        info2 = AuthorizedUserInfo(
            user_id=user.id,
            bank_id=bank.id,
            add_after_age_eighteen=False
        )
        
        created_info1 = au_repo.add_info(info1)
        created_info2 = au_repo.add_info(info2)
        
        # Act
        result = au_repo.get_all_info()
        
        # Assert
        assert len(result) == 2
        assert all(isinstance(info, AuthorizedUserInfo) for info in result)
        # Should be ordered by created_at DESC (most recent first)
        assert result[0].id == created_info2.id
        assert result[1].id == created_info1.id

    def test_get_all_info_with_limit(self, au_repo, clean_db, db_with_user_and_bank):
        """Test getting all authorized user info with limit"""
        # Arrange
        user, bank = db_with_user_and_bank
        
        for i in range(5):
            info = AuthorizedUserInfo(
                user_id=user.id,
                bank_id=bank.id,
                add_after_age_eighteen=True
            )
            au_repo.add_info(info)
        
        # Act
        result = au_repo.get_all_info(limit=3)
        
        # Assert
        assert len(result) == 3

    def test_get_all_info_with_offset(self, au_repo, clean_db, db_with_user_and_bank):
        """Test getting all authorized user info with offset"""
        # Arrange
        user, bank = db_with_user_and_bank
        
        for i in range(5):
            info = AuthorizedUserInfo(
                user_id=user.id,
                bank_id=bank.id,
                add_after_age_eighteen=True
            )
            au_repo.add_info(info)
        
        # Act
        result = au_repo.get_all_info(limit=2, offset=2)
        
        # Assert
        assert len(result) == 2

    def test_get_all_info_no_info(self, au_repo, clean_db):
        """Test getting all authorized user info when none exist"""
        # Act
        result = au_repo.get_all_info()
        
        # Assert
        assert result == []

    def test_info_exists_success(self, au_repo, clean_db, model_au_info):
        """Test checking if authorized user info exists"""
        # Arrange
        created_info = au_repo.add_info(model_au_info)
        
        # Act
        result = au_repo.info_exists(created_info.id)
        
        # Assert
        assert result is True

    def test_info_exists_not_found(self, au_repo, clean_db):
        """Test checking if non-existent authorized user info exists"""
        # Arrange
        non_existent_id = 99999
        
        # Act
        result = au_repo.info_exists(non_existent_id)
        
        # Assert
        assert result is False

    def test_get_info_count_success(self, au_repo, clean_db, db_with_user_and_bank):
        """Test getting count of authorized user info records"""
        # Arrange
        user, bank = db_with_user_and_bank
        
        info1 = AuthorizedUserInfo(
            user_id=user.id,
            bank_id=bank.id,
            add_after_age_eighteen=True
        )
        info2 = AuthorizedUserInfo(
            user_id=user.id,
            bank_id=bank.id,
            add_after_age_eighteen=False
        )
        
        au_repo.add_info(info1)
        au_repo.add_info(info2)
        
        # Act
        result = au_repo.get_info_count()
        
        # Assert
        assert result == 2

    def test_get_info_count_no_info(self, au_repo, clean_db):
        """Test getting count when no authorized user info exists"""
        # Act
        result = au_repo.get_info_count()
        
        # Assert
        assert result == 0

    def test_remove_all_info_by_user_success(self, au_repo, clean_db, db_with_user_and_bank):
        """Test removing all authorized user info for a user"""
        # Arrange
        user, bank = db_with_user_and_bank
        
        info1 = AuthorizedUserInfo(
            user_id=user.id,
            bank_id=bank.id,
            add_after_age_eighteen=True
        )
        info2 = AuthorizedUserInfo(
            user_id=user.id,
            bank_id=bank.id,
            add_after_age_eighteen=False
        )
        
        au_repo.add_info(info1)
        au_repo.add_info(info2)
        
        # Act
        result = au_repo.remove_all_info_by_user(user.id)
        
        # Assert
        assert result == 2
        
        # Verify all info is deleted
        remaining_info = au_repo.get_all_info_by_user(user.id)
        assert remaining_info == []

    def test_remove_all_info_by_user_no_info(self, au_repo, clean_db, db_with_user_and_bank):
        """Test removing all authorized user info for user with no info"""
        # Arrange
        user, bank = db_with_user_and_bank
        
        # Act
        result = au_repo.remove_all_info_by_user(user.id)
        
        # Assert
        assert result == 0

    def test_add_info_with_different_boolean_values(self, au_repo, clean_db, db_with_user_and_bank):
        """Test adding authorized user info with different boolean values"""
        # Arrange
        user, bank = db_with_user_and_bank
        
        info_true = AuthorizedUserInfo(
            user_id=user.id,
            bank_id=bank.id,
            add_after_age_eighteen=True
        )
        info_false = AuthorizedUserInfo(
            user_id=user.id,
            bank_id=bank.id,
            add_after_age_eighteen=False
        )
        
        # Act
        result_true = au_repo.add_info(info_true)
        result_false = au_repo.add_info(info_false)
        
        # Assert
        assert result_true.add_after_age_eighteen is True
        assert result_false.add_after_age_eighteen is False

    def test_update_info_all_fields(self, au_repo, clean_db, db_with_user_and_bank):
        """Test updating all fields of authorized user info"""
        # Arrange
        user, bank = db_with_user_and_bank
        
        # Create another user and bank for testing
        user_repo = UserRepository(os.getenv("TEST_DB_URL"))
        bank_repo = BankRepository(os.getenv("TEST_DB_URL"))
        
        user2 = User(name="User 2", email="user2@example.com", credit_score='none', annual_income=40000)
        bank2 = Bank(name="Bank 2", relationship_bank=False, reports_under_eighteen=True)
        
        created_user2 = user_repo.create_user(user2)
        created_bank2 = bank_repo.create_bank(bank2)
        
        original_info = AuthorizedUserInfo(
            user_id=user.id,
            bank_id=bank.id,
            add_after_age_eighteen=False
        )
        created_info = au_repo.add_info(original_info)
        
        # Modify all fields
        created_info.user_id = created_user2.id
        created_info.bank_id = created_bank2.id
        created_info.add_after_age_eighteen = True
        
        # Act
        result = au_repo.update_info(created_info)
        
        # Assert
        assert result is not None
        assert result.user_id == created_user2.id
        assert result.bank_id == created_bank2.id
        assert result.add_after_age_eighteen is True

    def test_get_info_by_user_and_bank_multiple_records(self, au_repo, clean_db, db_with_user_and_bank):
        """Test getting authorized user info by user and bank when multiple records exist"""
        # Arrange
        user, bank = db_with_user_and_bank
        
        # Create multiple records for same user-bank combination
        info1 = AuthorizedUserInfo(
            user_id=user.id,
            bank_id=bank.id,
            add_after_age_eighteen=True
        )
        info2 = AuthorizedUserInfo(
            user_id=user.id,
            bank_id=bank.id,
            add_after_age_eighteen=False
        )
        
        created_info1 = au_repo.add_info(info1)
        created_info2 = au_repo.add_info(info2)
        
        # Act
        result = au_repo.get_info_by_user_and_bank(user.id, bank.id)
        
        # Assert
        assert result is not None
        # Should return the first match found
        assert result.id in [created_info1.id, created_info2.id]