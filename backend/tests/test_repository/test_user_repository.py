import pytest
import psycopg
from src.model.user import User
from src.repository.user_repository import UserRepository

class TestUserRepository():

    def test_create_user(self, user_repo):
        """Test creating a new user"""

        user = User(
            id = None,
            name="Test User",
            email="test@example.com",
            annual_income=50000,
            credit_score="good",
            created_at=None
        )
        
        created_user = user_repo.create_user(user)
        
        assert created_user.id is not None
        assert created_user.name == "Test User"
        assert created_user.created_at is not None
