import psycopg
from typing import Optional, List
from model.user import User, SpendingCatagoryUser, AuthoritzedUserInfo

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
        with psycopg.connect("dbname=rewardInfo") as conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT * FROM users WHERE id = %s """, user_id)
                ...
                user_row = cur.fetchone()
                if not user_row:
                    return None
                
                cur.execute("""
                SELECT id, category, user_spend 
                FROM user_spending_category 
                WHERE user_id = %s
            """, (user_id,))
                
                spending_rows = cur.fetchall()

                # command to get authorized user info if any

                cur.execute("""
                SELECT id, bank_id, add_after_age_eighteen,
                FROM authorized_user_info 
                WHERE user_id = %s
            """, (user_id,))
                
                au_row = cur.fetchall()

                au_info = None

                if au_row:
                    au_info = AuthoritzedUserInfo (
                        id = au_row[0],
                        user_id = user_id,
                        bank_id = au_row[1],
                        add_after_age_eighteen = au_row[2]
                    )


                user = User(
                    id = user_row[0],
                    name = user_row[1],
                    email = user_row[2],
                    spending_catagories = [
                        SpendingCatagoryUser(id = spending_rows[0], category = spending_rows[1],
                                             user_spend = spending_rows[2]) for row in spending_rows],
                    authorized_user_info = au_info if au_info else None,
                    credit_score= user_row[3],
                    annual_income= user_row[4],
                    created_at= user_row[5]
                )

        
    def update_user(self, user_id: int, user_data: User) -> User:
        """Update user info (income, credit score, etc.)"""
        
    def delete_user(self, user_id: int) -> bool:
        """Soft delete or hard delete user"""
        
    def add_spending_category(self, user_id: int, spending: int) -> bool:
        """Add or update a spending category"""
        
    def remove_spending_category(self, user_id: int, category: str) -> bool:
        """Remove a spending category"""
        
    def get_users_by_credit_score(self, min_score: str) -> List[User]:
        """For analytics - get users by credit score range"""