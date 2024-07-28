CREATE TABLE IF NOT EXISTS Price (
    coinName VARCHAR(20), 
    fetch_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    price NUMERIC(15, 2) NOT NULL,
    PRIMARY KEY (coinName, fetch_timestamp)
);

CREATE TABLE IF NOT EXISTS AlertSubscription (
    email VARCHAR(50) NOT NULL,
    coinName VARCHAR(20),
    DifferencePercentage INT NOT NULL,
    PRIMARY KEY (email, coinName),
    FOREIGN KEY (coinName) REFERENCES Price(coinName)
);
