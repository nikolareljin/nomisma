-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Users table for authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for users
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Create sequence for inventory numbers
CREATE SEQUENCE coin_inventory_seq START 1;

-- Coins table
CREATE TABLE coins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Internal inventory tracking
    inventory_number VARCHAR(20) UNIQUE NOT NULL DEFAULT 'NOM-' || LPAD(nextval('coin_inventory_seq')::TEXT, 4, '0'),
    
    -- Basic information
    country VARCHAR(100),
    denomination VARCHAR(100),
    year INTEGER,
    mint_mark VARCHAR(20),
    composition VARCHAR(200),
    weight_grams DECIMAL(10, 3),
    diameter_mm DECIMAL(10, 2),
    
    -- Condition and grading
    condition_grade VARCHAR(50),
    condition_notes TEXT,
    defects TEXT,
    
    -- Cataloging
    catalog_number VARCHAR(100),
    variety VARCHAR(100),
    error_type VARCHAR(100),
    
    -- User notes
    notes TEXT,
    acquisition_date DATE,
    acquisition_price DECIMAL(10, 2),
    acquisition_source VARCHAR(200),
    
    -- Status
    is_for_sale BOOLEAN DEFAULT false,
    location VARCHAR(200)
);

-- Coin images table
CREATE TABLE coin_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    coin_id UUID NOT NULL REFERENCES coins(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    image_type VARCHAR(20), -- 'obverse', 'reverse', 'edge', 'detail'
    is_primary BOOLEAN DEFAULT false,
    
    -- Image metadata
    width INTEGER,
    height INTEGER,
    format VARCHAR(10)
);

-- AI analysis results
CREATE TABLE ai_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    coin_id UUID NOT NULL REFERENCES coins(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- AI identification
    identified_country VARCHAR(100),
    identified_denomination VARCHAR(100),
    identified_year INTEGER,
    identified_mint_mark VARCHAR(20),
    
    -- Condition assessment
    ai_grade VARCHAR(50),
    wear_level VARCHAR(50),
    surface_quality VARCHAR(50),
    strike_quality VARCHAR(50),
    luster_rating VARCHAR(50),
    
    -- Defects and errors
    detected_defects TEXT,
    detected_errors TEXT,
    
    -- Authenticity
    authenticity_assessment VARCHAR(50),
    authenticity_confidence DECIMAL(5, 2),
    
    -- Raw AI response
    raw_response JSONB,
    model_version VARCHAR(50)
);

-- Valuations table
CREATE TABLE valuations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    coin_id UUID NOT NULL REFERENCES coins(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Estimated values
    estimated_value_low DECIMAL(10, 2),
    estimated_value_high DECIMAL(10, 2),
    estimated_value_avg DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Valuation factors
    rarity_score INTEGER,
    condition_multiplier DECIMAL(5, 2),
    market_demand VARCHAR(50),
    
    -- Market data
    recent_sales_data JSONB,
    comparable_listings JSONB,
    
    -- Metadata
    valuation_source VARCHAR(100),
    confidence_level VARCHAR(50)
);

-- eBay listings table
CREATE TABLE ebay_listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    coin_id UUID NOT NULL REFERENCES coins(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- eBay data
    ebay_item_id VARCHAR(100) UNIQUE,
    listing_title VARCHAR(255),
    listing_description TEXT,
    starting_price DECIMAL(10, 2),
    buy_it_now_price DECIMAL(10, 2),
    
    -- Status
    status VARCHAR(50), -- 'draft', 'active', 'sold', 'ended', 'cancelled'
    listed_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    
    -- Sale information
    sold_price DECIMAL(10, 2),
    sold_at TIMESTAMP WITH TIME ZONE,
    buyer_username VARCHAR(100),
    
    -- eBay response
    ebay_response JSONB
);

-- Indexes for performance
CREATE INDEX idx_coins_inventory_number ON coins(inventory_number);
CREATE INDEX idx_coins_country ON coins(country);
CREATE INDEX idx_coins_year ON coins(year);
CREATE INDEX idx_coins_denomination ON coins(denomination);
CREATE INDEX idx_coins_condition_grade ON coins(condition_grade);
CREATE INDEX idx_coins_inventory_number ON coins(inventory_number);
CREATE INDEX idx_coins_user_id ON coins(user_id);
CREATE INDEX idx_ai_analyses_coin_id ON ai_analyses(coin_id);
CREATE INDEX idx_valuations_coin_id ON valuations(coin_id);
CREATE INDEX idx_ebay_listings_coin_id ON ebay_listings(coin_id);
CREATE INDEX idx_ebay_listings_status ON ebay_listings(status);

-- Full-text search indexes
CREATE INDEX idx_coins_notes_gin ON coins USING gin(to_tsvector('english', notes));
CREATE INDEX idx_coins_defects_gin ON coins USING gin(to_tsvector('english', defects));

-- Trigram indexes for fuzzy search
CREATE INDEX idx_coins_country_trgm ON coins USING gin(country gin_trgm_ops);
CREATE INDEX idx_coins_denomination_trgm ON coins USING gin(denomination gin_trgm_ops);

-- Updated at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to coins table
CREATE TRIGGER update_coins_updated_at BEFORE UPDATE ON coins
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
