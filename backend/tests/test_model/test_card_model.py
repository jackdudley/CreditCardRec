import pytest
from src.model.card import Card, RewardStructure
from src.model.enums import CardType
from pydantic import ValidationError
from datetime import datetime 

class TestCardModel():
    def test_create_card_with_valid_minimal_data(self):
        """Test creating card with minimal required fields"""
        card = Card(
            name="Chase Freedom",
            bank_id=1,
            card_type=CardType.STUDENT,
            reward_structure=RewardStructure.CASHBACK
        )
        
        assert card.name == "Chase Freedom"
        assert card.bank_id == 1
        assert card.card_type == CardType.STUDENT
        assert card.reward_structure == RewardStructure.CASHBACK
        assert card.id is None
        assert card.annual_fee == 0  # Default value
        assert card.created_at is None

    def test_create_card_with_all_fields(self):
        """Test creating card with all fields populated"""
        card = Card(
            id=123,
            name="Premium Travel Card",
            bank_id=2,
            card_type=CardType.BUSINESS,
            sub_max_value=75000,
            sub_description="75,000 points after $4,000 spend in 3 months",
            annual_fee=95,
            foreign_transaction_fee=2.7,
            reward_structure=RewardStructure.POINTS,
            fee_credits="Annual airline fee credit up to $200",
            other_benefits="Priority boarding, lounge access",
            created_at=datetime.now()
        )
        
        assert card.name == "Premium Travel Card"
        assert card.sub_max_value == 75000
        assert card.annual_fee == 95
        assert card.foreign_transaction_fee == 2.7
        assert card.fee_credits == "Annual airline fee credit up to $200"

    def test_card_missing_required_name_raises_error(self):
        """Test that missing name raises validation error"""
        with pytest.raises(ValidationError):
            Card(
                bank_id=1,
                card_type=CardType.STUDENT,
                reward_structure=RewardStructure.CASHBACK
                # Missing name - should fail
            )

    def test_card_missing_required_bank_id_raises_error(self):
        """Test that missing bank_id raises validation error"""
        with pytest.raises(ValidationError):
            Card(
                name="Test Card",
                card_type=CardType.STUDENT,
                reward_structure=RewardStructure.CASHBACK
                # Missing bank_id - should fail
            )

    def test_card_missing_required_card_type_raises_error(self):
        """Test that missing card_type raises validation error"""
        with pytest.raises(ValidationError):
            Card(
                name="Test Card",
                bank_id=1,
                reward_structure=RewardStructure.CASHBACK
                # Missing card_type - should fail
            )

    def test_card_missing_required_reward_structure_raises_error(self):
        """Test that missing reward_structure raises validation error"""
        with pytest.raises(ValidationError):
            Card(
                name="Test Card",
                bank_id=1,
                card_type=CardType.STUDENT
                # Missing reward_structure - should fail
            )

    def test_card_invalid_card_type_raises_error(self):
        """Test that invalid card_type raises validation error"""
        with pytest.raises(ValidationError):
            Card(
                name="Test Card",
                bank_id=1,
                card_type="invalid_type",  # Not a valid CardType enum
                reward_structure=RewardStructure.CASHBACK
            )

    def test_card_invalid_reward_structure_raises_error(self):
        """Test that invalid reward_structure raises validation error"""
        with pytest.raises(ValidationError):
            Card(
                name="Test Card",
                bank_id=1,
                card_type=CardType.STUDENT,
                reward_structure="invalid_reward"  # Not a valid RewardStructure enum
            )

    # def test_card_negative_annual_fee_raises_error(self):
    #     """Test that negative annual_fee raises validation error"""
    #     with pytest.raises(ValidationError):
    #         Card(
    #             name="Test Card",
    #             bank_id=1,
    #             card_type=CardType.STUDENT,
    #             reward_structure=RewardStructure.CASHBACK,
    #             annual_fee=-50  # Negative fee should be invalid
    #         )

    # def test_card_negative_foreign_transaction_fee_raises_error(self):
    #     """Test that negative foreign_transaction_fee raises validation error"""
    #     with pytest.raises(ValidationError):
    #         Card(
    #             name="Test Card",
    #             bank_id=1,
    #             card_type=CardType.STUDENT,
    #             reward_structure=RewardStructure.CASHBACK,
    #             foreign_transaction_fee=-1.5  # Negative fee should be invalid
    #         )

    # def test_card_empty_name_raises_error(self):
    #     """Test that empty name raises validation error"""
    #     with pytest.raises(ValidationError):
    #         Card(
    #             name="",  # Empty name should be invalid
    #             bank_id=1,
    #             card_type=CardType.STUDENT,
    #             reward_structure=RewardStructure.CASHBACK
    #         )

    def test_card_valid_card_types(self):
        """Test all valid card types work"""
        valid_types = [CardType.STUDENT, CardType.SECURED, CardType.BUSINESS]
        
        for card_type in valid_types:
            card = Card(
                name=f"Test {card_type.value} Card",
                bank_id=1,
                card_type=card_type,
                reward_structure=RewardStructure.CASHBACK
            )
            assert card.card_type == card_type

    def test_card_valid_reward_structures(self):
        """Test all valid reward structures work"""
        valid_structures = [RewardStructure.POINTS, RewardStructure.CASHBACK]
        
        for reward_structure in valid_structures:
            card = Card(
                name=f"Test {reward_structure.value} Card",
                bank_id=1,
                card_type=CardType.STUDENT,
                reward_structure=reward_structure
            )
            assert card.reward_structure == reward_structure

    def test_card_with_zero_annual_fee(self):
        """Test that zero annual fee is valid"""
        card = Card(
            name="Free Card",
            bank_id=1,
            card_type=CardType.STUDENT,
            reward_structure=RewardStructure.CASHBACK,
            annual_fee=0
        )
        assert card.annual_fee == 0

    def test_card_with_high_annual_fee(self):
        """Test that high annual fee is valid"""
        card = Card(
            name="Premium Card",
            bank_id=1,
            card_type=CardType.BUSINESS,
            reward_structure=RewardStructure.POINTS,
            annual_fee=695
        )
        assert card.annual_fee == 695

    def test_card_to_dict_conversion(self):
        """Test converting card to dictionary"""
        card = Card(
            name="Test Card",
            bank_id=1,
            card_type=CardType.STUDENT,
            reward_structure=RewardStructure.CASHBACK,
            annual_fee=50
        )
        
        card_dict = card.model_dump()
        
        assert card_dict["name"] == "Test Card"
        assert card_dict["bank_id"] == 1
        assert card_dict["annual_fee"] == 50
        assert card_dict["id"] is None