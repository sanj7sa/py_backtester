import os
import yfinance as yf
import pandas as pd
import sqlite3

class DataLoader:
    def __init__(self, db_name="market_data.db"):
        """
        Initialises the data loader. Sets up the database paths between the market data and data loader.
        """
        # Navigates from src/ to the data/ directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_dir = os.path.join(base_dir, "data")

        # Checks if the data directory exists
        os.makedirs(self.db_dir, exist_ok=True)

        self.db_path = os.path.join(self.db_dir, db_name)
    
    def _get_connection(self):
        """
        Creates a connection to the SQLite database.
        """
        return sqlite3.connect(self.db_path)
    
    def download_to_db(self, tickers, start_date, end_date, interval="1d"):
        """
        Downloads the historical data for a list of tickers with yfinance and saves each to its own table in SQLite database.
        """
        conn = self._get_connection()

        # Makes sure tickers are in list format
        if isinstance(tickers, str):
            tickers = [tickers]

        print(f"Starting data extraction into: {self.db_path}")

        for ticker in tickers:
            print(f"Fetching data for {ticker}...")
            try:
                # Downloads from yfinance
                df = yf.download(ticker, start=start_date, end=end_date, interval=interval)

                if df.empty:
                    print(f"## No data found for {ticker}. Will be skipped ##")
                    continue

                # Flatten MultiIndex columns if yfinance returns them
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                # Reset index so 'Date' becomes a regular column we can store
                df = df.reset_index()

                # Clean up column names to standard lowercase formatting
                df.columns = [col.lower().replace(" ", "_") for col in df.columns]

                # Save to SQLite. If the table already exists, it overwrites it with the new table.
                # Clean ticker string to avoid SQLite syntax issues with symbols like '^' or '='
                table_name = ticker.replace("^", "INDEX_").replace("=", "").replace("-", "_")
                df.to_sql(table_name, conn, if_exists="replace", index=False)

                print(f"Successfully saved {len(df)} rows to table '{table_name}'")
            except Exception as e:
                print(f"Failed to download {ticker}. Error: {e}")
            
        conn.close()
        print("Data extraction complete.")

    def load_data(self, ticker, start_date=None, end_date=None):
        """
        Retrieves historical data for a specific ticker from the local database.
        Returns a Pandas DataFrame formatted for backtesting.
        """
        # Reformatting the data to be in one specific format.
        table_name = ticker.replace("^", "INDEX_").replace("=", "").replace("-", "_")
        
        # Connects to the database
        conn = self._get_connection()
        
        # Selects the data from the SQL database
        query = f"SELECT * FROM {table_name}"

        try:
            # Connects the SQL query to the sqlite database
            df = pd.read_sql_query(query, conn)

            # Makes the date columns into objects for datetime not just text strings
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])

                # Filter by dates provided by a user
                if start_date:
                    df = df[df['date'] >= start_date]
                if end_date:
                    df = df[df['date'] <= end_date]
                
                # Make the date the "Index" so we can easily look up specific days later
                df.set_index('date', inplace=True)
            conn.close()
            return df
        
        except Exception as e:
            print(f"## Could not load data for {ticker}. Did you download it first? Error: {e} ##")
            conn.close()
            return None



# Execution test
if __name__ == "__main__":
    loader = DataLoader()

    # A mix of stocks and commodities with YFinance tickers
    # AAPL = Apple, GC=F = Gold Futures, MSFT = Microsoft
    test_tickers = ["AAPL", "MSFT", "GC=F"]
    loader.download_to_db(
        tickers=test_tickers, 
        start_date="2020-01-01", 
        end_date="2025-12-31"
    )
    print("\n--- Testing Data Extraction ---")
    
    # Test for Apple's data to see if it works
    aapl_data = loader.load_data("AAPL")
    
    if aapl_data is not None:
        print(f"Successfully loaded {len(aapl_data)} days of AAPL data.")
        print("Here are the first 3 days:")
        print(aapl_data.head(3)) # .head() prints the top rows of a DataFrame
