import pytest
import psycopg
from src.model.user import User, SpendingCategoryUser, AuthorizedUserInfo
from src.model.card import Bank
from src.model.enums import SpendingCategory
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

    def test_delete_user_success(self, user_repo, sample_user):

        #Arrange

        user = user_repo.create_user(sample_user)

        #Act

        delete_success = user_repo.delete_user(user.id)

        #Assert

        assert delete_success is True

    def test_delete_user_fail(self, user_repo, sample_user):

        #Arrange

        user = user_repo.create_user(sample_user)

        #Act

        delete_success = user_repo.delete_user(3000)

        #Assert

        assert delete_success is False

    def test_add_spending_catagory_success(self, user_repo, sample_user):

        #Arrange

        user = user_repo.create_user(sample_user)

        spending_cat = SpendingCategoryUser(
            user_id=user.id,
            category=SpendingCategory.GAS,
            user_spend=300
        )

        #Act

        result: SpendingCategoryUser = user_repo.add_spending_category(user.id, spending_cat)

        #Assert

        assert result.category==SpendingCategory.GAS
        assert result.user_id==user.id
        assert result.user_spend==300
        assert result.id is not None
        assert result.created_at is not None
        
    def test_remove_spending_catagory_success(self, user_repo, sample_user):

        #Arrange

        user = user_repo.create_user(sample_user)

        spending_cat = SpendingCategoryUser(
            user_id=user.id,
            category=SpendingCategory.GAS,
            user_spend=300
        )
        
        add: SpendingCategoryUser = user_repo.add_spending_category(user.id, spending_cat)

        #Act

        remove: bool = user_repo.remove_spending_category_by_id(add.id)

        #Assert

        assert remove is True
    
    def test_remove_spending_catagory_not_found(self, user_repo, sample_user):

        #Arrange

        user = user_repo.create_user(sample_user)

        spending_cat = SpendingCategoryUser(
            user_id=user.id,
            category=SpendingCategory.GAS,
            user_spend=300
        )
        
        add: SpendingCategoryUser = user_repo.add_spending_category(user.id, spending_cat)

        #Act

        remove: bool = user_repo.remove_spending_category_by_id(add.id+9999)

        #Assert
        
        assert remove is False
    # def test_add_authorized_user_info_AND DELETE TOO AFTER BANK ADDED(self, user_repo, sample_user):

        # CANT TEST UNTIL BANK/CARD REPO IS CREATED


    #     #Arrange

    #     user = user_repo.create_user(User(
    #     id=999,
    #     name="Updated User",
    #     email="updated@example.com",
    #     annual_income=100000,
    #     credit_score="excellent"
    #     ))

    #     auth = AuthorizedUserInfo (
    #         user_id=user.id,
    #         bank_id=1,
    #         add_after_age_eighteen=False
    #     )

    #     #Act

    #     auth_info: AuthorizedUserInfo = user_repo.add_authorized_user_info(auth)

    #     #Assert

    #     assert auth_info.user_id == user.id
    #     assert auth_info.add_after_age_eighteen == False
    #     assert auth_info.bank_id == 1
    #     assert auth_info.id is not None
    #     assert auth_info.created_at is not None

