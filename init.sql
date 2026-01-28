-- Initialize database for Expense Tracker
-- This file is executed when the PostgreSQL container starts for the first time

-- Create the test database
CREATE DATABASE expense_tracker_test;

-- Grant privileges to the user
GRANT ALL PRIVILEGES ON DATABASE expense_tracker TO expense_user;
GRANT ALL PRIVILEGES ON DATABASE expense_tracker_test TO expense_user;

-- Connect to the main database and create extensions if needed
\c expense_tracker;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Connect to the test database and create extensions if needed
\c expense_tracker_test;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
