CREATE TYPE credit_score AS ENUM ('excellent', 'good', 'fair', 'poor', 'none');
CREATE TYPE spending_category AS ENUM (
    'gas',
    'groceries', 
    'dining',
    'online_retail',
    'travel',
    'general',
    'rideshare',
    'public_transit',
    'entertainment'
);

CREATE TYPE reward_structure AS ENUM (
    'points',
    'cashback'
);

CREATE TYPE card_type AS ENUM (
    'student',
    'secured',
    'business',
    'general'
);
