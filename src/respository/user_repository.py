import psycopg
from typing import Optional, List
from model.user import User, SpendingCatagoryUser

class UserRepository:
    
    def create_user(self, user: User) -> User:
        """Create new user and return with ID"""
        with psycopg.connect("dbname=rewardInfo") as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO users (name, email, credit_score, annual_income, authorized_user_info)
                        VALUES (%s, %s, %s, %s, %s) RETURNING id, created_at
                        """, (user.name, user.email, user.credit_score, user.annual_income, user.authorized_user_info)
                    )
                    
                    result = cur.fetchone()
                    user.id = result[0]
                    user.created_at = result[1]

                    for spending in user.spending_categories:
                        cur.execute("""
                            INSERT INTO user_spending (user_id, category, monthly_amount)
                            VALUES (%s, %s, %s)
                        """, (user.id, spending.category, spending.user_spend))
                    
                        conn.commit()
                        return user
        
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