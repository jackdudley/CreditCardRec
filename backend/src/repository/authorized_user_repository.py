import psycopg, os
from datetime import datetime
from typing import Optional, List
from dotenv import load_dotenv
from src.model.user import AuthorizedUserInfo

load_dotenv()

class AuthorizedUserRepository():

    def __init__(self, database_url=None):
        self.database_url = database_url or os.getenv("DATABASE_URL")

    def add_info(self, au_info: AuthorizedUserInfo) -> AuthorizedUserInfo:
        """Create new info and return with ID"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO authorized_user_info (user_id, bank_id, add_after_age_eighteen)
                    VALUES (%s, %s, %s) RETURNING id, created_at
                    """, (au_info.user_id, au_info.bank_id, au_info.add_after_age_eighteen))
                result = cur.fetchone()
                au_info.id = result[0]
                au_info.created_at = result[1]
                conn.commit()
                return au_info

    def get_info_by_id(self, info_id: int) -> Optional[AuthorizedUserInfo]:
        """Get authorized user info by ID"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM authorized_user_info WHERE id = %s
                """, (info_id,))
                
                info_row = cur.fetchone()
                
                if not info_row:
                    return None
                
                return AuthorizedUserInfo(
                    id=info_row[0],
                    user_id=info_row[1],
                    bank_id=info_row[2],
                    add_after_age_eighteen=info_row[3],
                    created_at=info_row[4]
                )

    def remove_info(self, info_id: int) -> bool:
        """Remove authorized user info by ID. Returns True if removed, False if not found"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM authorized_user_info WHERE id = %s
                """, (info_id,))
                
                rows_affected = cur.rowcount
                conn.commit()
                
                return rows_affected > 0

    def get_all_info_by_user(self, user_id: int) -> List[AuthorizedUserInfo]:
        """Get all authorized user info for a specific user"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM authorized_user_info WHERE user_id = %s ORDER BY created_at DESC
                """, (user_id,))
                
                info_rows = cur.fetchall()
                
                return [
                    AuthorizedUserInfo(
                        id=row[0],
                        user_id=row[1],
                        bank_id=row[2],
                        add_after_age_eighteen=row[3],
                        created_at=row[4]
                    ) for row in info_rows
                ]

    def get_all_info_by_bank(self, bank_id: int) -> List[AuthorizedUserInfo]:
        """Get all authorized user info for a specific bank"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM authorized_user_info WHERE bank_id = %s ORDER BY created_at DESC
                """, (bank_id,))
                
                info_rows = cur.fetchall()
                
                return [
                    AuthorizedUserInfo(
                        id=row[0],
                        user_id=row[1],
                        bank_id=row[2],
                        add_after_age_eighteen=row[3],
                        created_at=row[4]
                    ) for row in info_rows
                ]

    def get_info_by_user_and_bank(self, user_id: int, bank_id: int) -> Optional[AuthorizedUserInfo]:
        """Get authorized user info for specific user and bank combination"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM authorized_user_info WHERE user_id = %s AND bank_id = %s
                """, (user_id, bank_id))
                
                info_row = cur.fetchone()
                
                if not info_row:
                    return None
                
                return AuthorizedUserInfo(
                    id=info_row[0],
                    user_id=info_row[1],
                    bank_id=info_row[2],
                    add_after_age_eighteen=info_row[3],
                    created_at=info_row[4]
                )

    def update_info(self, au_info: AuthorizedUserInfo) -> Optional[AuthorizedUserInfo]:
        """Update authorized user info"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE authorized_user_info 
                    SET user_id = %s, bank_id = %s, add_after_age_eighteen = %s
                    WHERE id = %s
                    RETURNING *
                """, (
                    au_info.user_id,
                    au_info.bank_id,
                    au_info.add_after_age_eighteen,
                    au_info.id
                ))
                
                updated_row = cur.fetchone()
                
                if not updated_row:
                    return None
                
                conn.commit()
                
                # Update the passed object with any DB changes
                au_info.created_at = updated_row[4]
                
                return au_info

   
    def get_all_info(self, limit: Optional[int] = None, offset: int = 0) -> List[AuthorizedUserInfo]:
        """Get all authorized user info with optional pagination"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                query = "SELECT * FROM authorized_user_info ORDER BY created_at DESC"
                params = []
                
                if limit:
                    query += " LIMIT %s OFFSET %s"
                    params.extend([limit, offset])
                elif offset > 0:
                    query += " OFFSET %s"
                    params.append(offset)
                    
                cur.execute(query, params)
                info_rows = cur.fetchall()
                
                return [
                    AuthorizedUserInfo(
                        id=row[0],
                        user_id=row[1],
                        bank_id=row[2],
                        add_after_age_eighteen=row[3],
                        created_at=row[4]
                    ) for row in info_rows
                ]

    def info_exists(self, info_id: int) -> bool:
        """Check if authorized user info exists by ID"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM authorized_user_info WHERE id = %s", (info_id,))
                return cur.fetchone() is not None

    def get_info_count(self) -> int:
        """Get total number of authorized user info records"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM authorized_user_info")
                return cur.fetchone()[0]

    def remove_all_info_by_user(self, user_id: int) -> int:
        """Remove all authorized user info for a specific user. Returns number of records removed"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM authorized_user_info WHERE user_id = %s
                """, (user_id,))
                
                rows_affected = cur.rowcount
                conn.commit()
                
                return rows_affected

