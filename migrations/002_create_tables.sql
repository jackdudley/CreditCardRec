CREATE TABLE users (
    id serial PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    credit_score credit_score_rating,
    annual_income INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE banks (
    id serial PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    relationship_bank boolean NOT NULL DEFAULT FALSE,
    transfer_points_value_cents DECIMAL(5,2),
    reports_under_eighteen boolean NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
)


CREATE TABLE credit_cards (
    id serial PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    bank_id INTEGER REFERENCES banks(id),
    card_type card_type NOT NULL,
    sub_max_value INTEGER,
    sub_description TEXT,
    annual_fee INTEGER NOT NULL DEFAULT 0,
    foreign_transaction_fee DECIMAL(5,3) NOT NULL DEFAULT 0.000,
    spending_categories spending_category[] NOT NULL,
    reward_structure reward_structure NOT NULL,
    fee_credits TEXT,
    other_benefits TEXT,
    created_at TIMESTAMP DEFAULT NOW()
)

CREATE TABLE card_spending_category (
    id serial PRIMARY KEY,
    card_id INTEGER REFERENCES credit_cards(id) ON DELETE CASCADE,
    category spending_category NOT NULL,
    rate DECIMAL(3,2),
    cap INTEGER,
    quarterly_rotating BOOLEAN NOT NULL DEFAULT FALSE
)

CREATE TABLE user_spending_category (
    id serial PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    category spending_category NOT NULL,
    user_spend INTEGER NOT NULL DEFAULT 0
)

CREATE TABLE authorized_user_info (
    id serial PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    bank_id  INTEGER REFERENCES banks(id),
    add_after_age_eighteen BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
)





