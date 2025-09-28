CREATE TABLE banks (
    id serial PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    relationship_bank boolean NOT NULL DEFAULT FALSE,
    transfer_points_value_cents DECIMAL(5,2),
    reports_under_eighteen boolean NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE credit_cards (
    id serial PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    bank_id INTEGER REFERENCES banks(id),
    card_type card_type NOT NULL,
    annual_fee INTEGER NOT NULL DEFAULT 0,
    foreign_transaction_fee DECIMAL(5,3) NOT NULL DEFAULT 0.000,
    reward_structure reward_structure NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE card_spending_category (
    id serial PRIMARY KEY,
    card_id INTEGER NOT NULL REFERENCES credit_cards(id) ON DELETE CASCADE,
    category spending_category_info NOT NULL,
    rate DECIMAL(3,2),
    cap INTEGER,
    quarterly_rotating BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (card_id, category)                      
);