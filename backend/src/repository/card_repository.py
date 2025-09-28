import os, json
from typing import Optional, List
import psycopg
from psycopg.rows import tuple_row
from src.model.card import Card, CardType, RewardStructure, SpendingCategoryInfo

def _enum_to_db(v):
    return None if v is None else getattr(v, "value", str(v))

def _enum_from_db(enum_cls, s):
    try:
        return enum_cls(s)
    except Exception:
        return s  # fallback if not strict

def _decode_spending(payload) -> List[SpendingCategoryInfo]:
    if payload in (None, "null"):
        return []
    data = payload if isinstance(payload, list) else json.loads(payload)
    return [SpendingCategoryInfo(**item) if isinstance(item, dict) else item for item in data]

def _encode_spending(items: List[SpendingCategoryInfo]):
    items = items or []
    return json.dumps([
        (i.model_dump() if hasattr(i, "model_dump") else (i.dict() if hasattr(i, "dict") else i))
        for i in items
    ])

class CardRepository:
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")

    def create_card(self, card: Card) -> Card:
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor(row_factory=tuple_row) as cur:
                cur.execute(
                    """
                    INSERT INTO credit_cards
                      (name, bank_id, card_type, annual_fee, foreign_transaction_fee, reward_structure, spending_categoies)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    RETURNING id, name, bank_id, card_type, annual_fee, foreign_transaction_fee,
                              reward_structure, spending_categoies, created_at
                    """,
                    (
                        card.name,
                        card.bank_id,
                        _enum_to_db(card.card_type),
                        card.annual_fee,
                        card.foreign_transaction_fee,
                        _enum_to_db(card.reward_structure),
                        _encode_spending(card.spending_categoies or []),
                    ),
                )
                row = cur.fetchone()
                conn.commit()
                return self._row_to_card(row)

    def get_card_by_id(self, card_id: int) -> Optional[Card]:
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor(row_factory=tuple_row) as cur:
                cur.execute(
                    """
                    SELECT id, name, bank_id, card_type, annual_fee, foreign_transaction_fee,
                           reward_structure, spending_categoies, created_at
                    FROM credit_cards
                    WHERE id = %s
                    """,
                    (card_id,),  # fixed 1-tuple
                )
                row = cur.fetchone()
                return self._row_to_card(row) if row else None

    def get_all_cards(self, limit: Optional[int] = None, offset: int = 0) -> List[Card]:
        sql = """
            SELECT id, name, bank_id, card_type, annual_fee, foreign_transaction_fee,
                   reward_structure, spending_categoies, created_at
            FROM credit_cards
            ORDER BY created_at DESC
        """
        params: List = []
        if limit is not None:
            sql += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])
        elif offset > 0:
            sql += " OFFSET %s"
            params.append(offset)

        with psycopg.connect(self.database_url) as conn:
            with conn.cursor(row_factory=tuple_row) as cur:
                cur.execute(sql, params)
                return [self._row_to_card(r) for r in cur.fetchall()]

    def get_cards_by_bank(self, bank_id: int) -> List[Card]:
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor(row_factory=tuple_row) as cur:
                cur.execute(
                    """
                    SELECT id, name, bank_id, card_type, annual_fee, foreign_transaction_fee,
                           reward_structure, spending_categoies, created_at
                    FROM credit_cards
                    WHERE bank_id = %s
                    ORDER BY name
                    """,
                    (bank_id,),  # fixed 1-tuple
                )
                return [self._row_to_card(r) for r in cur.fetchall()]

    def update_card(self, card: Card) -> Optional[Card]:
        if card.id is None:
            return None
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor(row_factory=tuple_row) as cur:
                cur.execute(
                    """
                    UPDATE credit_cards
                       SET name = %s,
                           bank_id = %s,
                           card_type = %s,
                           annual_fee = %s,
                           foreign_transaction_fee = %s,
                           reward_structure = %s,
                           spending_categoies = %s
                     WHERE id = %s
                 RETURNING id, name, bank_id, card_type, annual_fee, foreign_transaction_fee,
                           reward_structure, spending_categoies, created_at
                    """,
                    (
                        card.name,
                        card.bank_id,
                        _enum_to_db(card.card_type),
                        card.annual_fee,
                        card.foreign_transaction_fee,
                        _enum_to_db(card.reward_structure),
                        _encode_spending(card.spending_categoies or []),
                        card.id,
                    ),
                )
                row = cur.fetchone()
                if not row:
                    conn.rollback()
                    return None
                conn.commit()
                return self._row_to_card(row)

    def delete_card(self, card_id: int) -> bool:
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM credit_cards WHERE id = %s", (card_id,))  # fixed 1-tuple
                deleted = cur.rowcount > 0
                conn.commit()
                return deleted

    def _row_to_card(self, r) -> Card:
        return Card(
            id=r[0],
            name=r[1],
            bank_id=r[2],
            card_type=_enum_from_db(CardType, r[3]),
            annual_fee=r[4],
            foreign_transaction_fee=r[5],
            reward_structure=_enum_from_db(RewardStructure, r[6]),
            spending_categoies=_decode_spending(r[7]),
            created_at=r[8],
        )
