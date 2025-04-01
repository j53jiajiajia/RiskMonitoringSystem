-- 1. Create Positions Table
CREATE TABLE IF NOT EXISTS positions (
    id SERIAL PRIMARY KEY,
    client_id INT NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    quantity INT NOT NULL,
    cost_basis DECIMAL(10,2) NOT NULL
);

-- 2. Create Market Data Table
CREATE TABLE IF NOT EXISTS market_data (
    symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    current_price NUMERIC(12, 2) NOT NULL,
    PRIMARY KEY (symbol, timestamp)
);

-- 3. Create Margin Table
CREATE TABLE IF NOT EXISTS margin (
    client_id INT PRIMARY KEY,
    loan DECIMAL(10,2) NOT NULL,
    margin_requirement DECIMAL(10,2)
);