import psycopg
import psycopg
from typing import Optional, List
from src.model.card import Bank
import os
from dotenv import load_dotenv

load_dotenv()

class BankRepository():

    def __init__(self, database_url=None):
        self.database_url = database_url or os.getenv("DATABASE_URL")

    def create_bank(self, bank: Bank) -> Bank:
            """Create new bank and return it back"""
            with psycopg.connect(self.database_url) as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO banks (name, relationship_bank, transfer_points_value_cents, reports_under_eighteen) 
                            VALUES (%s, %s, %s, %s) RETURNING id, created_at
                            """, (bank.name, bank.relationship_bank, bank.transfer_points_value_cents, bank.reports_under_eighteen)
                        )

                        result = cur.fetchone()
                        bank.id = result[0]
                        bank.created_at = result[1]
                        
                        conn.commit()
                        return bank
    def get_bank_by_id(self, bank_id: int) -> Optional[Bank]:
        """Retrieve a bank by its ID"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM banks WHERE id = %s
                """, (bank_id,))
                
                bank_row = cur.fetchone()
                
                if not bank_row:
                    return None
                
                return Bank(
                    id=bank_row[0],
                    name=bank_row[1],
                    relationship_bank=bank_row[2],
                    transfer_points_value_cents=bank_row[3],
                    reports_under_eighteen=bank_row[4],
                    created_at=bank_row[5]
                )

    def update_bank(self, bank: Bank) -> Optional[Bank]:
        """Update a bank with all fields"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE banks 
                    SET name = %s, relationship_bank = %s, transfer_points_value_cents = %s, 
                        reports_under_eighteen = %s
                    WHERE id = %s
                    RETURNING *
                """, (
                    bank.name,
                    bank.relationship_bank,
                    bank.transfer_points_value_cents,
                    bank.reports_under_eighteen,
                    bank.id
                ))
                
                updated_row = cur.fetchone()
                
                if not updated_row:
                    return None
                
                conn.commit()
                
                # Update the passed bank object with any DB changes
                bank.created_at = updated_row[5]
                
                return bank

    def delete_bank(self, bank_id: int) -> bool:
        """Delete a bank by ID. Returns True if deleted, False if not found"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM banks WHERE id = %s
                """, (bank_id,))
                
                rows_affected = cur.rowcount
                conn.commit()
                
                return rows_affected > 0

    def get_all_banks(self, limit: Optional[int] = None, offset: int = 0) -> List[Bank]:
        """Get all banks with optional pagination"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                query = "SELECT * FROM banks ORDER BY name"
                params = []
                
                if limit:
                    query += " LIMIT %s OFFSET %s"
                    params.extend([limit, offset])
                elif offset > 0:
                    query += " OFFSET %s"
                    params.append(offset)
                    
                cur.execute(query, params)
                bank_rows = cur.fetchall()
                
                return [
                    Bank(
                        id=row[0],
                        name=row[1],
                        relationship_bank=row[2],
                        transfer_points_value_cents=row[3],
                        reports_under_eighteen=row[4],
                        created_at=row[5]
                    ) for row in bank_rows
                ]

    def get_relationship_banks(self) -> List[Bank]:
        """Get all banks that are relationship banks"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM banks WHERE relationship_bank = true ORDER BY name
                """)
                
                bank_rows = cur.fetchall()
                
                return [
                    Bank(
                        id=row[0],
                        name=row[1],
                        relationship_bank=row[2],
                        transfer_points_value_cents=row[3],
                        reports_under_eighteen=row[4],
                        created_at=row[5]
                    ) for row in bank_rows
                ]

    def get_banks_that_report_under_eighteen(self) -> List[Bank]:
        """Get all banks that report accounts for users under 18"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM banks WHERE reports_under_eighteen = true ORDER BY name
                """)
                
                bank_rows = cur.fetchall()
                
                return [
                    Bank(
                        id=row[0],
                        name=row[1],
                        relationship_bank=row[2],
                        transfer_points_value_cents=row[3],
                        reports_under_eighteen=row[4],
                        created_at=row[5]
                    ) for row in bank_rows
                ]

    def get_banks_with_transfer_points(self) -> List[Bank]:
        """Get all banks that have transfer points value set"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM banks 
                    WHERE transfer_points_value_cents IS NOT NULL 
                    ORDER BY transfer_points_value_cents DESC
                """)
                
                bank_rows = cur.fetchall()
                
                return [
                    Bank(
                        id=row[0],
                        name=row[1],
                        relationship_bank=row[2],
                        transfer_points_value_cents=row[3],
                        reports_under_eighteen=row[4],
                        created_at=row[5]
                    ) for row in bank_rows
                ]
    def bank_exists(self, bank_id: int) -> bool:
        """Check if a bank exists by ID"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM banks WHERE id = %s", (bank_id,))
                return cur.fetchone() is not None

    def get_bank_by_name(self, name: str) -> Optional[Bank]:
        """Get a bank by exact name match"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM banks WHERE name = %s
                """, (name,))
                
                bank_row = cur.fetchone()
                
                if not bank_row:
                    return None
                
                return Bank(
                    id=bank_row[0],
                    name=bank_row[1],
                    relationship_bank=bank_row[2],
                    transfer_points_value_cents=bank_row[3],
                    reports_under_eighteen=bank_row[4],
                    created_at=bank_row[5]
                )