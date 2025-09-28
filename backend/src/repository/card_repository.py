import os
from typing import Optional, List
import psycopg
from psycopg.rows import tuple_row

from src.model.card import (
    Card,
    CardType,
    RewardStructure,
    CardSpendingCategory,  # <- use the card-level category model
)
from src.model.enums import SpendingCategoryType as SpendingCategoryEnum  # adjust if your name differs


def _enum_to_db(v):
    return None if v is None else getattr(v, "value", str(v))

def _enum_from_db(enum_cls, s):
    try:
        return enum_cls(s)
    except Exception:
        return s  # fallback if not strict


class CardRepository:
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")

    # ---------- CREATE ----------
    def create_card(self, card: Card) -> Card:
        """
        Inserts a card, then inserts its spending categories into card_spending_category.
        """
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor(row_factory=tuple_row) as cur:
                cur.execute(
                    """
                    INSERT INTO credit_cards
                        (name, bank_id, card_type, annual_fee, foreign_transaction_fee, reward_structure)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, name, bank_id, card_type, annual_fee, foreign_transaction_fee, reward_structure, created_at
                    """,
                    (
                        card.name,
                        card.bank_id,
                        _enum_to_db(card.card_type),
                        card.annual_fee,
                        card.foreign_transaction_fee,
                        _enum_to_db(card.reward_structure),
                    ),
                )
                row = cur.fetchone()
                card_id = row[0]

                for sc in (card.spending_categories or []):
                    cur.execute(
                        """
                        INSERT INTO card_spending_category
                            (card_id, category, rate, cap, quarterly_rotating)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (card_id, category) DO UPDATE
                          SET rate = EXCLUDED.rate,
                              cap = EXCLUDED.cap,
                              quarterly_rotating = EXCLUDED.quarterly_rotating
                        """,
                        (
                            card_id,
                            _enum_to_db(getattr(sc, "category", None)),
                            getattr(sc, "rate", None),
                            getattr(sc, "cap", None),
                            getattr(sc, "quarterly_rotating", False),
                        ),
                    )

                conn.commit()

                created = self._row_to_card(row)
                created.spending_categories = self._get_card_categories_by_conn(cur, card_id)
                return created

    def get_card_by_id(self, card_id: int) -> Optional[Card]:
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor(row_factory=tuple_row) as cur:
                cur.execute(
                    """
                    SELECT id, name, bank_id, card_type, annual_fee, foreign_transaction_fee, reward_structure, created_at
                    FROM credit_cards
                    WHERE id = %s
                    """,
                    (card_id,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                card = self._row_to_card(row)
                card.spending_categories = self._get_card_categories_by_conn(cur, card.id)
                return card

    def get_all_cards(self, limit: Optional[int] = None, offset: int = 0) -> List[Card]:
        sql = """
            SELECT id, name, bank_id, card_type, annual_fee, foreign_transaction_fee, reward_structure, created_at
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
                cards = [self._row_to_card(r) for r in cur.fetchall()]
                for c in cards:
                    c.spending_categories = self._get_card_categories_by_conn(cur, c.id)
                return cards

    def get_cards_by_bank(self, bank_id: int) -> List[Card]:
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor(row_factory=tuple_row) as cur:
                cur.execute(
                    """
                    SELECT id, name, bank_id, card_type, annual_fee, foreign_transaction_fee, reward_structure, created_at
                    FROM credit_cards
                    WHERE bank_id = %s
                    ORDER BY name
                    """,
                    (bank_id,),
                )
                cards = [self._row_to_card(r) for r in cur.fetchall()]
                for c in cards:
                    c.spending_categories = self._get_card_categories_by_conn(cur, c.id)
                return cards

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
                           reward_structure = %s
                     WHERE id = %s
                 RETURNING id, name, bank_id, card_type, annual_fee, foreign_transaction_fee, reward_structure, created_at
                    """,
                    (
                        card.name,
                        card.bank_id,
                        _enum_to_db(card.card_type),
                        card.annual_fee,
                        card.foreign_transaction_fee,
                        _enum_to_db(card.reward_structure),
                        card.id,
                    ),
                )
                row = cur.fetchone()
                if not row:
                    conn.rollback()
                    return None

                cur.execute("DELETE FROM card_spending_category WHERE card_id = %s", (card.id,))
                for sc in (card.spending_categories or []):
                    cur.execute(
                        """
                        INSERT INTO card_spending_category
                            (card_id, category, rate, cap, quarterly_rotating)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (card_id, category) DO UPDATE
                          SET rate = EXCLUDED.rate,
                              cap = EXCLUDED.cap,
                              quarterly_rotating = EXCLUDED.quarterly_rotating
                        """,
                        (
                            card.id,
                            _enum_to_db(getattr(sc, "category", None)),
                            getattr(sc, "rate", None),
                            getattr(sc, "cap", None),
                            getattr(sc, "quarterly_rotating", False),
                        ),
                    )

                conn.commit()

                updated = self._row_to_card(row)
                updated.spending_categories = self._get_card_categories_by_conn(cur, card.id)
                return updated

    def delete_card(self, card_id: int) -> bool:
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                # child rows will be deleted by ON DELETE CASCADE (if set)
                cur.execute("DELETE FROM credit_cards WHERE id = %s", (card_id,))
                deleted = cur.rowcount > 0
                conn.commit()
                return deleted

    def _get_card_categories_by_conn(self, cur, card_id: int) -> List[CardSpendingCategory]:
        cur.execute(
            """
            SELECT id, category, rate, cap, quarterly_rotating
            FROM card_spending_category
            WHERE card_id = %s
            ORDER BY category
            """,
            (card_id,),
        )
        rows = cur.fetchall()
        out: List[CardSpendingCategory] = []
        for r in rows:
            out.append(
                CardSpendingCategory(
                    id=r[0],
                    category=_enum_from_db(SpendingCategoryEnum, r[1]),
                    rate=r[2],
                    cap=r[3],
                    quarterly_rotating=r[4],
                )
            )
        return out

    def _row_to_card(self, r) -> Card:
        return Card(
            id=r[0],
            name=r[1],
            bank_id=r[2],
            card_type=_enum_from_db(CardType, r[3]),
            annual_fee=r[4],
            foreign_transaction_fee=r[5],
            reward_structure=_enum_from_db(RewardStructure, r[6]),
            created_at=r[7],
            spending_categories=[],
        )
    
