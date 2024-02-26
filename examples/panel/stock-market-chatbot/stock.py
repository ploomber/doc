import yfinance as yf
import duckdb
import os
import pandas as pd

# Define the stock symbols you're interested in
stock_symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "FB"]

# Define the date range
start_date = "2014-01-01"
end_date = "2024-02-22"

# Database file path
db_file = "stockdata.duckdb"

def get_stock_data(ticker, start_date, end_date):
    """
    Downloads stock data for a given symbol between the specified date range.
    """
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

def store_data_in_duckdb(ticker, data):
    """
    Stores the downloaded stock data into a DuckDB database.
    """
    conn = duckdb.connect(db_file)
    # Convert the index (Date) to a column since DuckDB will use it as such
    data.reset_index(inplace=True)
    # Use the DataFrame.to_sql() method for efficient data storage
    data.to_sql(ticker.lower(), conn, if_exists='replace', index=False)
    conn.close()

def main():
    """
    Main function to download stock data and store it in DuckDB.
    """
    for ticker in stock_symbols:
        print(f"Downloading data for {ticker}...")
        data = get_stock_data(ticker, start_date, end_date)
        print(f"Storing data for {ticker} in DuckDB...")
        store_data_in_duckdb(ticker, data)
        print(f"Data for {ticker} stored successfully.")

if __name__ == "__main__":
    main()
