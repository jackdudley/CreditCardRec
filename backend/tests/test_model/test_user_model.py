import pytest
from src.model.user import User, CreditScoreRating
from pydantic import ValidationError
class TestUserModel():

    def test_create_user_with_valid_data(self):
        """Test creating user with all valid fields"""
        user = User(
            id=None,
            name="John Doe",
            email="john@example.com",
            credit_score="excellent",
            annual_income=75000,
            created_at=None
        )
        
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.annual_income == 75000
        assert user.credit_score == "excellent"
        assert user.id is None 
        assert user.created_at is None

    def test_user_invalid_email(self):
        """Test invalid email raises error"""
        with pytest.raises(ValidationError):
            User(name="John", email="invalid-email", credit_score="good", annual_income=4000)
    
    def test_user_invalid_name(self):
        """Test invalid email raises error"""
        with pytest.raises(ValidationError):
            User(name="123", email="invalid-email", credit_score="good", annual_income=4000)
    
    def test_user_invalid_score(self):
        """Test invalid email raises error"""
        with pytest.raises(ValidationError):
            User(name="Test", email="1@gmail.com", credit_score="definately_not_valid", annual_income=4000)

    def test_user_invalid_income(self):
        """Test invalid email raises error"""
        with pytest.raises(ValidationError):
            User(name="Test", email="1@gmail.com", credit_score="definately_not_valid", annual_income="a")