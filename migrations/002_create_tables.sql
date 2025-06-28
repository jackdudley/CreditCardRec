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
    reports_under_eighteen boolean NOT NULL DEFAULT FALSE
    created_at TIMESTAMP DEFAULT NOW()
)


CREATE TABLE credit_cards (
    id serial PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    bank INTEGER REFERENCES banks(id),
    card_type card_type,

)

CREATE TABLE sign_up_bonus (
    id serial PRIMARY KEY,
    card_id INTEGER REFERENCES credit_cards(id),
    deadline_days INTEGER NOT NULL,
    spend_required INTEGER NOT NULL,
    value_dollars DECIMAL(7,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()

)





