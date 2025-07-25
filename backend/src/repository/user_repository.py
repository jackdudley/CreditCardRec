import psycopg
from typing import Optional, List
from src.model.user import User, SpendingCategoryUser, AuthorizedUserInfo
import os
from dotenv import load_dotenv

load_dotenv()

class UserRepository:

    def __init__(self, database_url=None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
    
    def create_user(self, user: User) -> User:
        """Create new user and return with ID"""
        with psycopg.connect(self.database_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO users (name, email, credit_score, annual_income)
                        VALUES (%s, %s, %s, %s) RETURNING id, created_at
                        """, (user.name, user.email, user.credit_score, user.annual_income)
                    )
                    
                    result = cur.fetchone()
                    user.id = result[0]
                    user.created_at = result[1]
                    
                    conn.commit()
                    return user
        
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user with all spending categories"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT * FROM users WHERE id=%s """, (user_id,))
                ...
                user_row = cur.fetchone()

                if not user_row:
                    return None

                user = User(
                    id = user_row[0],
                    name = user_row[1],
                    email = user_row[2],
                    credit_score= user_row[3],
                    annual_income= user_row[4],
                    created_at= user_row[5]
                )

                conn.commit()

                return user

        
    def update_user(self, user_data: User) -> User:
        """Update user info (income, credit score, etc.)"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """UPDATE users SET name=%s, email=%s, credit_score=%s, annual_income=%s
                    WHERE id=%s""", (user_data.name, user_data.email, user_data.credit_score, 
                    user_data.annual_income, user_data.id))
        
                updated_row = cur.rowcount

                conn.commit()

                if not updated_row:
                    return None

                return self.get_user_by_id(user_data.id)

        
    def delete_user(self, user_id: int) -> bool:
        """Soft delete or hard delete user"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""DELETE FROM users WHERE id=%s""", (user_id,))

                deleted_user = cur.rowcount

                conn.commit()

                if(deleted_user):
                    return True
                else:
                    return False
        
    def add_spending_category(self, spending: SpendingCategoryUser) -> SpendingCategoryUser:
        """Add or update a spending category"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                            INSERT INTO user_spending_category (user_id, category, user_spend)
                            VALUES (%s, %s, %s) RETURNING id, created_at
                            """, (spending.user_id, spending.category, spending.user_spend)
                            )
                
                added_category = cur.rowcount
                
                spending_row = cur.fetchone()
                spending.id = spending_row[0]
                spending.created_at = spending_row[1]

                conn.commit()

                if(added_category):
                    return spending
                else:
                    return None
                

    def remove_spending_category_by_id(self, user_category_id: int) -> bool:
        """Remove a spending category"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                            DELETE FROM user_spending_category
                            WHERE id=%s
                            """, (user_category_id,))
                
                deleted_category = cur.rowcount

                conn.commit()

                if(deleted_category):
                    return True
                else:
                    return False

    def add_authorized_user_info(self, au_info: AuthorizedUserInfo) -> AuthorizedUserInfo:
        """add authorized user info"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:   

                cur.execute("""
                            INSERT INTO authorized_user_info (user_id, bank_id, add_after_age_eighteen)
                            VALUES (%s,%s,%s) RETURNING id
                            """, (au_info.user_id, au_info.bank_id, au_info.add_after_age_eighteen))
                
                inserted_row = cur.fetchone()

                au_info.id = inserted_row[0]

                conn.commit()

                return au_info
                
        
    def delete_authorized_user_info(self, au_id: int) -> bool:
        """delete authorized user info"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                            DELETE FROM authorized_user_info
                            WHERE id=%s
                            """, (au_id,))
                
                deleted_info = cur.rowcount
                conn.commit()
                if(deleted_info):
                    return True
                else:
                    return False
    def get_spending_categories_by_user(self, user_id) -> List[SpendingCategoryUser]:
        """Get spending category by a given user id"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                            SELECT * FROM user_spending_category WHERE user_id=%s ORDER BY id
                            """, (user_id,))
                
                retrieved_info = cur.fetchall()
                return_list = [SpendingCategoryUser(
                    id=row[0],
                    user_id=row[1],
                    category=row[2],
                    user_spend=row[3],
                    created_at=row[4]
                ) for row in retrieved_info]
                conn.commit()
                if(retrieved_info):
                    return return_list
                else:
                    return []
            