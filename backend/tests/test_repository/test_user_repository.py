import pytest
import psycopg
from src.model.user import User
from src.respository.user_repository import UserRepository

class TestUserRepository():

    def test_create_user(self, user_repo):
        """Test creating a new user"""
        user = User(
            name="Test User",
            email="test@example.com",
            annual_income=50000
        )
        
        created_user = user_repo.create_user(user)
        
        assert created_user.id is not None
        assert created_user.name == "Test User"
