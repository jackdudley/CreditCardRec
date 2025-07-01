import psycopg
from typing import Optional, List
from src.model.card import Card, SpendingCategory, CardType, RewardStructure
import os
from dotenv import load_dotenv

load_dotenv()

class CardRepository:

    def __init__(self, database_url=None):
        self.database_url = database_url or os.getenv("DATABASE_URL")

    def create_card(self, card: Card) -> Card:
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO credit_cards (name, bank_id, card_type, sub_max_value, sub_description, foreign_transaction_fee, annual_fee, reward_structure,
                            fee_credits, other_benefits) VALUES
                            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id, created_at
                            """, (card.name, card.bank_id, card.card_type, card.sub_max_value, card.sub_description, card.foreign_transaction_fee, card.annual_fee, card.reward_structure,
                            card.fee_credits, card.other_benefits)
                            )

                row_add = cur.fetchone()
                card.id = row_add[0]
                card.created_at = row_add[1]

                conn.commit()

                return card
            
    def get_card_by_id(self, card_id: int) -> Card:
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM credit_cards WHERE id=%s
                """, (card_id,))
                
                card_row = cur.fetchone()
                
                if not card_row:
                    return None
                
                card = Card(
                    id=card_row[0],
                    name=card_row[1],
                    bank_id=card_row[2],
                    card_type=card_row[3],
                    sub_max_value=card_row[4],
                    sub_description=card_row[5],
                    annual_fee=card_row[6],
                    foreign_transaction_fee=card_row[7],
                    reward_structure=card_row[8],
                    fee_credits=card_row[9],
                    other_benefits=card_row[10],
                    created_at=card_row[11]
                )
                
                return card
    def update_card(self, card: Card) -> Optional[Card]:
        """Update a card with all fields"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE credit_cards
                    SET name = %s, bank_id = %s, card_type = %s, sub_max_value = %s, 
                        sub_description = %s, annual_fee = %s, foreign_transaction_fee = %s,
                        reward_structure = %s, fee_credits = %s, other_benefits = %s
                    WHERE id = %s
                    RETURNING *
                """, (
                    card.name,
                    card.bank_id,
                    card.card_type,
                    card.sub_max_value,
                    card.sub_description,
                    card.annual_fee,
                    card.foreign_transaction_fee,
                    card.reward_structure,
                    card.fee_credits,
                    card.other_benefits,
                    card.id
                ))
                
                updated_row = cur.fetchone()
                
                if not updated_row:
                    return None
                
                conn.commit()
                
                # Update the passed card object with any DB changes
                card.created_at = updated_row[11]
                
                return card
            

    def delete_card(self, card_id: int) -> bool:
        """Delete a card by ID. Returns True if deleted, False if not found"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM credit_cards WHERE id = %s
                """, (card_id,))
                
                rows_affected = cur.rowcount
                conn.commit()
                
                return rows_affected > 0
            
    def get_cards_by_bank(self, bank_id: int) -> List[Card]:
        """Get allcredit_cardsfor a specific bank"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM credit_cards WHERE bank_id = %s ORDER BY name
                """, (bank_id,))
                
                card_rows = cur.fetchall()
                
                return [
                    Card(
                        id=row[0],
                        name=row[1],
                        bank_id=row[2],
                        card_type=row[3],
                        sub_max_value=row[4],
                        sub_description=row[5],
                        annual_fee=row[6],
                        foreign_transaction_fee=row[7],
                        reward_structure=row[8],
                        fee_credits=row[9],
                        other_benefits=row[10],
                        created_at=row[11]
                    ) for row in card_rows
                ]
    def get_cards_by_type(self, card_type: CardType) -> List[Card]:
        """Get all credit cards of a specific type"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM credit_cards WHERE card_type = %s ORDER BY name
                """, (card_type,))
                
                card_rows = cur.fetchall()
                
                return [
                    Card(
                        id=row[0],
                        name=row[1],
                        bank_id=row[2],
                        card_type=row[3],
                        sub_max_value=row[4],
                        sub_description=row[5],
                        annual_fee=row[6],
                        foreign_transaction_fee=row[7],
                        reward_structure=row[8],
                        fee_credits=row[9],
                        other_benefits=row[10],
                        created_at=row[11]
                    ) for row in card_rows
                ]
            
    def get_cards_by_reward_structure(self, reward_structure: RewardStructure) -> List[Card]:
        """Get all credit cards with a specific reward structure"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM credit_cards WHERE reward_structure = %s ORDER BY name
                """, (reward_structure,))
                
                card_rows = cur.fetchall()
                
                return [
                    Card(
                        id=row[0],
                        name=row[1],
                        bank_id=row[2],
                        card_type=row[3],
                        sub_max_value=row[4],
                        sub_description=row[5],
                        annual_fee=row[6],
                        foreign_transaction_fee=row[7],
                        reward_structure=row[8],
                        fee_credits=row[9],
                        other_benefits=row[10],
                        created_at=row[11]
                    ) for row in card_rows
                ]
    def get_cards_with_no_annual_fee(self) -> List[Card]:
        """Get all credit cards with no annual fee"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM credit_cards WHERE annual_fee = 0 ORDER BY name
                """)
                
                card_rows = cur.fetchall()
                
                return [
                    Card(
                        id=row[0],
                        name=row[1],
                        bank_id=row[2],
                        card_type=row[3],
                        sub_max_value=row[4],
                        sub_description=row[5],
                        annual_fee=row[6],
                        foreign_transaction_fee=row[7],
                        reward_structure=row[8],
                        fee_credits=row[9],
                        other_benefits=row[10],
                        created_at=row[11]
                    ) for row in card_rows
                ]
    def get_cards_with_signup_bonus(self) -> List[Card]:
        """Get all credit cards that have a signup bonus (sub_max_value > 0)"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM credit_cards
                    WHERE sub_max_value IS NOT NULL AND sub_max_value > 0 
                    ORDER BY sub_max_value DESC
                """)
                
                card_rows = cur.fetchall()
                
                return [
                    Card(
                        id=row[0],
                        name=row[1],
                        bank_id=row[2],
                        card_type=row[3],
                        sub_max_value=row[4],
                        sub_description=row[5],
                        annual_fee=row[6],
                        foreign_transaction_fee=row[7],
                        reward_structure=row[8],
                        fee_credits=row[9],
                        other_benefits=row[10],
                        created_at=row[11]
                    ) for row in card_rows
                ]
            
    def get_all_cards(self, limit: Optional[int] = None, offset: int = 0) -> List[Card]:
        """Get all credit cards with optional pagination"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                query = "SELECT * FROM credit_cards ORDER BY created_at DESC"
                params = []

                if limit:
                    query += " LIMIT %s OFFSET %s"
                    params.extend([limit, offset])
                elif offset > 0:
                    query += " OFFSET %s"
                    params.append(offset)
                    
                cur.execute(query, params)
                card_rows = cur.fetchall()
                
                return [
                    Card(
                        id=row[0],
                        name=row[1],
                        bank_id=row[2],
                        card_type=row[3],
                        sub_max_value=row[4],
                        sub_description=row[5],
                        annual_fee=row[6],
                        foreign_transaction_fee=row[7],
                        reward_structure=row[8],
                        fee_credits=row[9],
                        other_benefits=row[10],
                        created_at=row[11]
                    ) for row in card_rows
                ]
            
    def get_cards_by_fee_range(self, min_fee: int = 0, max_fee: Optional[int] = None) -> List[Card]:
        """Get credit cards within a specific annual fee range"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                if max_fee is not None:
                    cur.execute("""
                        SELECT * FROM credit_cards
                        WHERE annual_fee >= %s AND annual_fee <= %s 
                        ORDER BY annual_fee, name
                    """, (min_fee, max_fee))
                else:
                    cur.execute("""
                        SELECT * FROM credit_cards
                        WHERE annual_fee >= %s 
                        ORDER BY annual_fee, name
                    """, (min_fee,))
                
                card_rows = cur.fetchall()
                
                return [
                    Card(
                        id=row[0],
                        name=row[1],
                        bank_id=row[2],
                        card_type=row[3],
                        sub_max_value=row[4],
                        sub_description=row[5],
                        annual_fee=row[6],
                        foreign_transaction_fee=row[7],
                        reward_structure=row[8],
                        fee_credits=row[9],
                        other_benefits=row[10],
                        created_at=row[11]
                    ) for row in card_rows
                ]