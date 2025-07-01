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
                            INSERT INTO banks (name, relationship_bank, reports_under_eighteen) 
                            VALUES (%s, %s, %s) RETURNING id, created_at
                            """, (bank.name, bank.relationship_bank, bank.reports_under_eighteen)
                        )

                        result = cur.fetchone()
                        bank.id = result[0]
                        bank.created_at = result[1]
                        
                        conn.commit()
                        return bank