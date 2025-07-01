import os
import pytest
import psycopg
from dotenv import load_dotenv
from src.model.user import User
from src.repository.user_repository import UserRepository

load_dotenv()

@pytest.fixture
def test_db_connection():
    """Create a test database connection"""
    conn = psycopg.connect(os.getenv("TEST_DB_URL"))
    yield conn
    conn.close()

@pytest.fixture(autouse=True)
def clean_db(test_db_connection):
    """Clean database before each test"""
    with test_db_connection.cursor() as cur:
        cur.execute("TRUNCATE users, banks, credit_cards, card_spending_category, authorized_user_info, user_spending_category RESTART IDENTITY CASCADE")
    test_db_connection.commit()
    yield test_db_connection

@pytest.fixture
def user_repo():
    """Create UserRepository instance for testing"""
    return UserRepository(os.getenv("TEST_DB_URL"))

@pytest.fixture
def sample_user():
    """Create a sample user for testing"""
    return User(
        name="Test User",
        email="test@example.com",
        annual_income=50000,
        credit_score="good"
    )