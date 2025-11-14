-- ResoftAI Development Database Initialization Script
-- This script is run automatically when the PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create test database
CREATE DATABASE resoftai_test;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE resoftai_dev TO postgres;
GRANT ALL PRIVILEGES ON DATABASE resoftai_test TO postgres;

-- Connect to main dev database
\c resoftai_dev;

-- Create helpful functions for development
CREATE OR REPLACE FUNCTION updated_at_trigger()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'ResoftAI development database initialized successfully!';
END $$;
