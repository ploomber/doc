import yfinance as yf
import duckdb
import os
import pandas as pd
import requests 

# Database file path
db_file = "stockdata.duckdb"

def get_stock_symbols():
# Symbols obtained from 
# https://www.nasdaq.com/market-activity/stocks/screener
    data = pd.read_csv("nasdaq_symbols.csv")
    symbols = data["Symbol"].to_list()
    names = data['Name'].to_list()

    symbol_name = {symbol: name for symbol, name in zip(symbols, names)}

    return symbols, symbol_name


def get_stock_data(ticker, start_date, end_date):
    """
    Downloads stock data for a given symbol between the specified date range.
    
    Parameters:
    - ticker: Stock ticker symbol as a string.
    - start_date: Start date as a 'YYYY-MM-DD' string or datetime object.
    - end_date: End date as a 'YYYY-MM-DD' string or datetime object.
    """
    start_date_str = start_date.value.strftime('%Y-%m-%d')
    end_date_str = end_date.value.strftime('%Y-%m-%d')

    data = yf.download(ticker, start=start_date_str, end=end_date_str)
    return data

def store_data_in_duckdb(tickers, start_date, end_date, db_file="stockdata.duckdb"):
    """
    Stores the downloaded stock data for multiple tickers into a DuckDB database.

    Parameters:
    - tickers: List of stock ticker symbols as strings.
    - start_date: Start date for the data download.
    - end_date: End date for the data download.
    - db_file: The path to the DuckDB database file.
    """
    # Delete the existing database file if it exists
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Deleted existing database file: {db_file}")
    conn = duckdb.connect(db_file)
    
    for ticker in tickers:
        try:
            data = get_stock_data(ticker, start_date, end_date)
            
            # Ensure the DataFrame has a 'Date' column
            if data.index.name == 'Date' or 'Date' not in data.columns:
                data.reset_index(inplace=True)
            
            table_name = ticker.lower()
            # Directly use DuckDB's method to insert the DataFrame
            conn.register('temp_df', data)
            conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM temp_df")
            print(f"Data for '{ticker}' stored successfully in '{db_file}' in the table '{table_name}'.")
            
        except Exception as e:   
            pass
            print(f"Error storing data for '{ticker}': {e}") 
    conn.close()
    
def get_data_from_duckdb(nl_query, tickers, start_date, end_date, db_file="stockdata.duckdb"):
    """
    Converts a natural language query into SQL and fetches data from DuckDB.
    """
    combined_data = pd.DataFrame()
    for ticker in tickers:
        try:
            sql_query = """SELECT {nl_query}, Date
                            FROM {ticker}
                            WHERE Date >= '{start_date}' AND Date <= '{end_date}'""".format(nl_query=nl_query, 
                                                                                            ticker=ticker, 
                                                                                            start_date=start_date, 
                                                                                            end_date=end_date)

            conn = duckdb.connect(db_file)
            data = conn.execute(sql_query).fetchdf()
            conn.close()
            # Optionally, add a column to identify the ticker symbol in the combined DataFrame
            data['Ticker'] = ticker
            combined_data = pd.concat([combined_data, data], ignore_index=True)
        except Exception as e:
            pass 
    
    return combined_data