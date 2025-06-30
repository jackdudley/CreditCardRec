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
                SELECT * FROM users WHERE id = %s """, (user_id,))
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

                cur.execute("""
                SELECT id, bank_id, add_after_age_eighteen,
                FROM authorized_user_info 
                WHERE user_id = %s
            """, (user_id,))
                
                au_row = cur.fetchall()

                au_info = []

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
                                             user_spend = row[2]) for row in spending_rows],
                    authorized_user_info = au_info if au_info else [],
                    credit_score= user_row[3],
                    annual_income= user_row[4],
                    created_at= user_row[5]
                )

                conn.commit()

                return user

        
    def update_user(self, user_id: int, user_data: User) -> User:
        """Update user info (income, credit score, etc.)"""
        with psycopg.connect("dbname=rewardInfo") as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """UPDATE users SET (name=%s, email=%s, credit_score=%s, annual_income=%s )
                    WHERE user_id=%s""", (user_data.name, user_data.email, user_data.credit_score, 
                    user_data.annual_income, user_id))
        
                updated_row = cur.fetchone()

                conn.commit()

                if not updated_row:
                    return None

                return self.get_user_by_id(user_id)

        
    def delete_user(self, user_id: int) -> bool:
        """Soft delete or hard delete user"""
        with psycopg.connect("dbname=rewardInfo") as conn:
            with conn.cursor() as cur:
                cur.execute("""DELETE FROM users WHERE user_id=%s""", (user_id,))

                deleted_user = cur.rowcount

                conn.commit()

                if(deleted_user):
                    return True
                else:
                    return False
        
    def add_spending_category(self, user_id: int, spending: SpendingCatagoryUser) -> bool:
        """Add or update a spending category"""
        with psycopg.connect("dbname=rewardInfo") as conn:
            with conn.cursor() as cur:
                cur.execute("""
                            INSERT INTO user_spending_category (catagory, user_spend)
                            VALUES %s, %s WHERE user_id=%s
                            """, (spending.catagory, spending.user_spend, user_id))
                
                added_catagory = cur.rowcount

                conn.commit()

                if(added_catagory):
                    return True
                else:
                    return False
                

    def remove_spending_category(self, user_id: int, category: SpendingCatagoryUser) -> bool:
        """Remove a spending category"""
        with psycopg.connect("dbname=rewardInfo") as conn:
            with conn.cursor() as cur:
                cur.execute("""
                            DELETE FROM user_spending_category
                            WHERE user_id=%s AND catagory=%s
                            """, (category, user_id))
                
                deleted_catagory = cur.rowcount

                conn.commit()

                if(deleted_catagory):
                    return True
                else:
                    return False

    def add_authorized_user_info(self, au_info: AuthoritzedUserInfo) -> AuthoritzedUserInfo:
        """add authorized user info"""
        with psycopg.connect("dbname=rewardInfo") as conn:
            with conn.cursor() as cur:   

                cur.execute("""
                            INSERT INTO authorized_user_info (user_id, bank_id, add_after_eighteen)
                            VALUES %s,%s,%s RETURNING id
                            """, au_info.user_id, au_info.bank_id, au_info.add_after_age_eighteen)
                
                inserted_row = cur.fetchone()

                au_info = AuthoritzedUserInfo (
                    id = inserted_row[0],
                    user_id = au_info.user_id,
                    bank_id = au_info.bank_id,
                    add_after_age_eighteen = au_info.add_after_age_eighteen
                )

                conn.commit()

                return au_info
                

                
        
    def delete_authorized_user_info(self, au_id: int) -> bool:
        """delete authorized user info"""
        with psycopg.connect("dbname=rewardInfo") as conn:
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
