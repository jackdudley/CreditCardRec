import pytest, psycopg, os
from unittest.mock import Mock, patch
from datetime import datetime
from dotenv import load_dotenv
from src.model.enums import CardType, RewardStructure
from src.repository.card_repository import CardRepository
from src.repository.bank_repository import BankRepository
from src.model.card import Bank, Card

load_dotenv()

class TestCardRepository():

    @pytest.fixture
    def test_db_connection(self):
        """Create a test database connection"""
        conn = psycopg.connect(os.getenv("TEST_DB_URL"))
        yield conn
        conn.close()

    @pytest.fixture
    def card_repo(self):
        return CardRepository(os.getenv("TEST_DB_URL"))
    

    @pytest.fixture
    def model_card(self):
        return Card(
        name='Chase Sapphire Preferred',
        bank_id=1,
        card_type=CardType.GENERAL,
        sub_max_value=60000,
        sub_description='Spend $4000 in first 3 months',
        annual_fee=95,
        foreign_transaction_fee=0.0,
        reward_structure=RewardStructure.POINTS,
        fee_credits='2x points on travel',
        other_benefits='Priority Pass lounge access',
    )
    
    
    @pytest.fixture()
    def clean_db(self, test_db_connection):
        """Clean database before each test"""
        with test_db_connection.cursor() as cur:
            cur.execute("TRUNCATE users, banks, credit_cards, card_spending_category, authorized_user_info, user_spending_category RESTART IDENTITY CASCADE")
        test_db_connection.commit()
        yield test_db_connection

    @pytest.fixture
    def db_with_bank(self):
        bank_repo = BankRepository(database_url=os.getenv("TEST_DB_URL"))
        bank: Bank = Bank(
            name="Chase",
            relationship_bank=True,
            reports_under_eighteen=False
        )

        bank_repo.create_bank(bank)

    def test_create_card(self, card_repo, clean_db, db_with_bank, model_card):    
        #Act
        card = card_repo.create_card(model_card)
        
        #Assert
        assert card is not None
        assert isinstance(card, Card)
        
        assert card.id is not None
        assert isinstance(card.id, int)
        assert card.id > 0
        
        assert card.name == model_card.name
        assert card.bank_id == model_card.bank_id
        assert card.card_type == model_card.card_type
        assert card.sub_max_value == model_card.sub_max_value
        assert card.sub_description == model_card.sub_description
        assert card.annual_fee == model_card.annual_fee
        assert card.foreign_transaction_fee == model_card.foreign_transaction_fee
        assert card.reward_structure == model_card.reward_structure
        assert card.fee_credits == model_card.fee_credits
        assert card.other_benefits == model_card.other_benefits
        
        assert card.created_at is not None
        assert isinstance(card.created_at, datetime)
        
        assert model_card.id == card.id
        assert model_card.created_at == card.created_at
        
        assert card is model_card

    def test_get_card_by_id_success(self, card_repo, clean_db, db_with_bank, model_card):
        """Test successfully retrieving a card by ID"""
        # Arrange
        created_card = card_repo.create_card(model_card)
        
        # Act
        result = card_repo.get_card_by_id(created_card.id)
        
        # Assert
        assert result is not None
        assert isinstance(result, Card)
        assert result.id == created_card.id
        assert result.name == created_card.name
        assert result.bank_id == created_card.bank_id
        assert result.card_type == created_card.card_type
        assert result.sub_max_value == created_card.sub_max_value
        assert result.sub_description == created_card.sub_description
        assert result.annual_fee == created_card.annual_fee
        assert result.foreign_transaction_fee == created_card.foreign_transaction_fee
        assert result.reward_structure == created_card.reward_structure
        assert result.fee_credits == created_card.fee_credits
        assert result.other_benefits == created_card.other_benefits
        assert result.created_at == created_card.created_at
    
    def test_get_card_by_id_not_found(self, card_repo, clean_db):
        """Test retrieving a card that doesn't exist"""
        # Arrange
        non_existent_id = 99999
        
        # Act
        result = card_repo.get_card_by_id(non_existent_id)
        
        # Assert
        assert result is None
    
    def test_get_card_by_id_with_none_values(self, card_repo, clean_db, db_with_bank):
        """Test retrieving a card with optional None values"""
        # Arrange
        minimal_card = Card(
            name="Basic Card",
            bank_id=1,
            card_type=CardType.GENERAL,
            sub_max_value=None,
            sub_description=None,
            annual_fee=0,
            foreign_transaction_fee=0.0,
            reward_structure=RewardStructure.CASHBACK,
            fee_credits=None,
            other_benefits=None
        )
        created_card = card_repo.create_card(minimal_card)
        
        # Act
        result = card_repo.get_card_by_id(created_card.id)
        
        # Assert
        assert result is not None
        assert result.id == created_card.id
        assert result.name == "Basic Card"
        assert result.sub_max_value is None
        assert result.sub_description is None
        assert result.foreign_transaction_fee == 0.0
        assert result.fee_credits is None
        assert result.other_benefits is None
        assert result.annual_fee == 0

    def test_update_card_success(self, card_repo, clean_db, db_with_bank, model_card):
        """Test successfully updating a card"""
        # Arrange
        created_card = card_repo.create_card(model_card)
        
        # Modify the card
        created_card.name = "Updated Card Name"
        created_card.annual_fee = 150
        created_card.other_benefits = "Updated benefits"
        
        # Act
        result = card_repo.update_card(created_card)
        
        # Assert
        assert result is not None
        assert isinstance(result, Card)
        assert result.id == created_card.id
        assert result.name == "Updated Card Name"
        assert result.annual_fee == 150
        assert result.other_benefits == "Updated benefits"
        assert result.created_at == created_card.created_at
        assert result is created_card  # Same object reference

    def test_update_card_not_found(self, card_repo, clean_db):
        """Test updating a card that doesn't exist"""
        # Arrange
        non_existent_card = Card(
            id=99999,
            name="Non-existent Card",
            bank_id=1,
            card_type=CardType.GENERAL,
            annual_fee=100,
            reward_structure=RewardStructure.POINTS
        )
        
        # Act
        result = card_repo.update_card(non_existent_card)
        
        # Assert
        assert result is None

    def test_delete_card_success(self, card_repo, clean_db, db_with_bank, model_card):
        """Test successfully deleting a card"""
        # Arrange
        created_card = card_repo.create_card(model_card)
        
        # Act
        result = card_repo.delete_card(created_card.id)
        
        # Assert
        assert result is True
        
        # Verify card is deleted
        deleted_card = card_repo.get_card_by_id(created_card.id)
        assert deleted_card is None

    def test_delete_card_not_found(self, card_repo, clean_db):
        """Test deleting a card that doesn't exist"""
        # Arrange
        non_existent_id = 99999
        
        # Act
        result = card_repo.delete_card(non_existent_id)
        
        # Assert
        assert result is False

    def test_get_cards_by_bank_success(self, card_repo, clean_db, db_with_bank):
        """Test getting cards by bank ID"""
        # Arrange
        card1 = Card(
            name="Bank Card 1",
            bank_id=1,
            card_type=CardType.GENERAL,
            annual_fee=50,
            reward_structure=RewardStructure.POINTS
        )
        card2 = Card(
            name="Bank Card 2",
            bank_id=1,
            card_type=CardType.GENERAL,
            annual_fee=100,
            reward_structure=RewardStructure.CASHBACK
        )
        
        card_repo.create_card(card1)
        card_repo.create_card(card2)
        
        # Act
        result = card_repo.get_cards_by_bank(1)
        
        # Assert
        assert len(result) == 2
        assert all(isinstance(card, Card) for card in result)
        assert all(card.bank_id == 1 for card in result)
        # Should be ordered by name
        assert result[0].name == "Bank Card 1"
        assert result[1].name == "Bank Card 2"

    def test_get_cards_by_bank_no_cards(self, card_repo, clean_db):
        """Test getting cards for bank with no cards"""
        # Act
        result = card_repo.get_cards_by_bank(999)
        
        # Assert
        assert result == []

    def test_get_cards_by_type_success(self, card_repo, clean_db, db_with_bank):
        """Test getting cards by card type"""
        # Arrange
        card1 = Card(
            name="General Card",
            bank_id=1,
            card_type=CardType.GENERAL,
            annual_fee=50,
            reward_structure=RewardStructure.POINTS
        )
        card2 = Card(
            name="Business Card",
            bank_id=1,
            card_type=CardType.BUSINESS,
            annual_fee=100,
            reward_structure=RewardStructure.CASHBACK
        )
        
        card_repo.create_card(card1)
        card_repo.create_card(card2)
        
        # Act
        result = card_repo.get_cards_by_type(CardType.GENERAL)
        
        # Assert
        assert len(result) == 1
        assert result[0].card_type == CardType.GENERAL
        assert result[0].name == "General Card"

    def test_get_cards_by_type_no_cards(self, card_repo, clean_db):
        """Test getting cards for type with no cards"""
        # Act
        result = card_repo.get_cards_by_type(CardType.BUSINESS)
        
        # Assert
        assert result == []

    def test_get_cards_by_reward_structure_success(self, card_repo, clean_db, db_with_bank):
        """Test getting cards by reward structure"""
        # Arrange
        card1 = Card(
            name="Points Card",
            bank_id=1,
            card_type=CardType.GENERAL,
            annual_fee=50,
            reward_structure=RewardStructure.POINTS
        )
        card2 = Card(
            name="Cashback Card",
            bank_id=1,
            card_type=CardType.GENERAL,
            annual_fee=0,
            reward_structure=RewardStructure.CASHBACK
        )
        
        card_repo.create_card(card1)
        card_repo.create_card(card2)
        
        # Act
        result = card_repo.get_cards_by_reward_structure(RewardStructure.POINTS)
        
        # Assert
        assert len(result) == 1
        assert result[0].reward_structure == RewardStructure.POINTS
        assert result[0].name == "Points Card"

    def test_get_cards_by_reward_structure_no_cards(self, card_repo, clean_db):
        """Test getting cards for reward structure with no cards"""
        # Act
        result = card_repo.get_cards_by_reward_structure(RewardStructure.POINTS)
        
        # Assert
        assert result == []

    def test_get_cards_with_no_annual_fee_success(self, card_repo, clean_db, db_with_bank):
        """Test getting cards with no annual fee"""
        # Arrange
        card1 = Card(
            name="Free Card",
            bank_id=1,
            card_type=CardType.GENERAL,
            annual_fee=0,
            reward_structure=RewardStructure.CASHBACK
        )
        card2 = Card(
            name="Premium Card",
            bank_id=1,
            card_type=CardType.GENERAL,
            annual_fee=95,
            reward_structure=RewardStructure.POINTS
        )
        
        card_repo.create_card(card1)
        card_repo.create_card(card2)
        
        # Act
        result = card_repo.get_cards_with_no_annual_fee()
        
        # Assert
        assert len(result) == 1
        assert result[0].annual_fee == 0
        assert result[0].name == "Free Card"

    def test_get_cards_with_no_annual_fee_no_cards(self, card_repo, clean_db):
        """Test getting no annual fee cards when none exist"""
        # Act
        result = card_repo.get_cards_with_no_annual_fee()
        
        # Assert
        assert result == []

    def test_get_cards_with_signup_bonus_success(self, card_repo, clean_db, db_with_bank):
        """Test getting cards with signup bonus"""
        # Arrange
        card1 = Card(
            name="Bonus Card High",
            bank_id=1,
            card_type=CardType.GENERAL,
            annual_fee=95,
            sub_max_value=80000,
            reward_structure=RewardStructure.POINTS
        )
        card2 = Card(
            name="Bonus Card Low",
            bank_id=1,
            card_type=CardType.GENERAL,
            annual_fee=0,
            sub_max_value=20000,
            reward_structure=RewardStructure.CASHBACK
        )
        card3 = Card(
            name="No Bonus Card",
            bank_id=1,
            card_type=CardType.GENERAL,
            annual_fee=0,
            sub_max_value=None,
            reward_structure=RewardStructure.CASHBACK
        )
        
        card_repo.create_card(card1)
        card_repo.create_card(card2)
        card_repo.create_card(card3)
        
        # Act
        result = card_repo.get_cards_with_signup_bonus()
        
        # Assert
        assert len(result) == 2
        # Should be ordered by sub_max_value DESC
        assert result[0].sub_max_value == 80000
        assert result[1].sub_max_value == 20000
        assert result[0].name == "Bonus Card High"
        assert result[1].name == "Bonus Card Low"

    def test_get_cards_with_signup_bonus_no_cards(self, card_repo, clean_db):
        """Test getting signup bonus cards when none exist"""
        # Act
        result = card_repo.get_cards_with_signup_bonus()
        
        # Assert
        assert result == []

    def test_get_all_cards_success(self, card_repo, clean_db, db_with_bank):
        """Test getting all cards without pagination"""
        # Arrange
        card1 = Card(
            name="Card 1",
            bank_id=1,
            card_type=CardType.GENERAL,
            annual_fee=0,
            reward_structure=RewardStructure.CASHBACK
        )
        card2 = Card(
            name="Card 2",
            bank_id=1,
            card_type=CardType.GENERAL,
            annual_fee=95,
            reward_structure=RewardStructure.POINTS
        )
        
        created_card1 = card_repo.create_card(card1)
        created_card2 = card_repo.create_card(card2)
        
        # Act
        result = card_repo.get_all_cards()
        
        # Assert
        assert len(result) == 2
        assert all(isinstance(card, Card) for card in result)
        # Should be ordered by created_at DESC (most recent first)
        assert result[0].id == created_card2.id
        assert result[1].id == created_card1.id

    def test_get_all_cards_with_limit(self, card_repo, clean_db, db_with_bank):
        """Test getting all cards with limit"""
        # Arrange
        for i in range(5):
            card = Card(
                name=f"Card {i}",
                bank_id=1,
                card_type=CardType.GENERAL,
                annual_fee=0,
                reward_structure=RewardStructure.CASHBACK
            )
            card_repo.create_card(card)
        
        # Act
        result = card_repo.get_all_cards(limit=3)
        
        # Assert
        assert len(result) == 3

    def test_get_all_cards_with_offset(self, card_repo, clean_db, db_with_bank):
        """Test getting all cards with offset"""
        # Arrange
        for i in range(5):
            card = Card(
                name=f"Card {i}",
                bank_id=1,
                card_type=CardType.GENERAL,
                annual_fee=0,
                reward_structure=RewardStructure.CASHBACK
            )
            card_repo.create_card(card)
        
        # Act
        result = card_repo.get_all_cards(limit=2, offset=2)
        
        # Assert
        assert len(result) == 2

    def test_get_all_cards_no_cards(self, card_repo, clean_db):
        """Test getting all cards when none exist"""
        # Act
        result = card_repo.get_all_cards()
        
        # Assert
        assert result == []

    def test_get_cards_by_fee_range_with_max(self, card_repo, clean_db, db_with_bank):
        """Test getting cards within fee range with max"""
        # Arrange
        card1 = Card(
            name="Free Card",
            bank_id=1,
            card_type=CardType.GENERAL,
            annual_fee=0,
            reward_structure=RewardStructure.CASHBACK
        )
        card2 = Card(
            name="Mid Card",
            bank_id=1,
            card_type=CardType.GENERAL,
            annual_fee=95,
            reward_structure=RewardStructure.POINTS
        )
        card3 = Card(
            name="Premium Card",
            bank_id=1,
            card_type=CardType.GENERAL,
            annual_fee=550,
            reward_structure=RewardStructure.POINTS
        )
        
        card_repo.create_card(card1)
        card_repo.create_card(card2)
        card_repo.create_card(card3)
        
        # Act
        result = card_repo.get_cards_by_fee_range(min_fee=0, max_fee=100)
        
        # Assert
        assert len(result) == 2
        assert all(0 <= card.annual_fee <= 100 for card in result)
        # Should be ordered by annual_fee, then name
        assert result[0].annual_fee == 0
        assert result[1].annual_fee == 95

    def test_get_cards_by_fee_range_without_max(self, card_repo, clean_db, db_with_bank):
        """Test getting cards within fee range without max"""
        # Arrange
        card1 = Card(
            name="Free Card",
            bank_id=1,
            card_type=CardType.GENERAL,
            annual_fee=0,
            reward_structure=RewardStructure.CASHBACK
        )
        card2 = Card(
            name="Premium Card",
            bank_id=1,
            card_type=CardType.GENERAL,
            annual_fee=550,
            reward_structure=RewardStructure.POINTS
        )
        
        card_repo.create_card(card1)
        card_repo.create_card(card2)
        
        # Act
        result = card_repo.get_cards_by_fee_range(min_fee=100)
        
        # Assert
        assert len(result) == 1
        assert result[0].annual_fee >= 100
        assert result[0].name == "Premium Card"

    def test_get_cards_by_fee_range_no_cards(self, card_repo, clean_db):
        """Test getting cards in fee range when none exist in range"""
        # Act
        result = card_repo.get_cards_by_fee_range(min_fee=1000, max_fee=2000)
        
        # Assert
        assert result == []