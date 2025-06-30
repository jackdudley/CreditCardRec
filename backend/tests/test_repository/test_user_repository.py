import pytest
import psycopg
from src.model.user import User
from src.repository.user_repository import UserRepository

class TestUserRepository():

    def test_create_user(self, user_repo):
        """Test creating a new user"""

        user = User(
            name="Test User",
            email="test@example.com",
            annual_income=50000,
            credit_score="good",
        )
        
        created_user = user_repo.create_user(user)
        
        assert created_user.id is not None
        assert created_user.name == "Test User"
        assert created_user.created_at is not None
    
    def test_get_user_by_id_found(self, user_repo, sample_user):

        #Arrange

        user = user_repo.create_user(sample_user)


        #Act

        user_test = user_repo.get_user_by_id(user.id)

        #Assert

        assert user.id == user_test.id

    def test_get_user_by_id_not_found(self, user_repo, sample_user):

        #Arrange

        user = user_repo.create_user(sample_user)


        #Act

        user_test = user_repo.get_user_by_id(user.id+1)

        #Assert

        assert user_test is None

    def test_update_user_found(self, user_repo, sample_user):

        #Arrange

        user_og = user_repo.create_user(sample_user)


        user_updated = User(
        id=user_og.id,
        name="Updated User",
        email="updated@example.com",
        annual_income=100000,
        credit_score="excellent"
        )

        #Act

        updated_user = user_repo.update_user(user_updated)

        #Assert

        assert updated_user == user_updated

    def test_update_user_not_found(self, user_repo, sample_user):

        #Arrange

        user_repo.create_user(sample_user)

        user_updated = User(
        id=999,
        name="Updated User",
        email="updated@example.com",
        annual_income=100000,
        credit_score="excellent"
        )

        #Act

        updated_user = user_repo.update_user(user_updated)

        #Assert

        assert updated_user is None

        


