import psycopg
from typing import Optional, List
from model.user import User, SpendingAmount

class UserRepository:
    
    def create_user(self, user: User) -> User:
        """Create new user and return with ID"""
        
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user with all spending categories"""
        
    def update_user(self, user_id: int, user_data: User) -> User:
        """Update user info (income, credit score, etc.)"""
        
    def delete_user(self, user_id: int) -> bool:
        """Soft delete or hard delete user"""
        
    def add_spending_category(self, user_id: int, spending: SpendingAmount) -> bool:
        """Add or update a spending category"""
        
    def remove_spending_category(self, user_id: int, category: str) -> bool:
        """Remove a spending category"""
        
    def get_users_by_credit_score(self, min_score: str) -> List[User]:
        """For analytics - get users by credit score range"""