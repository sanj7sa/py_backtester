import pandas as pd
import numpy as np

from strategies.base_strategy import BaseStrategy

class MovingAverageCrossStrategy(BaseStrategy):
    """
    A Trend-Following strategy. 
    It buys when a fast moving average crosses above a slow moving average.
    """
    def __init__(self, short_window=50, long_window=200, name="MA Crossover"):
        # Gets the parent strategy to be executed first
        super().__init__(name)

        # Defines the parameters for our strategy
        self.short_window = short_window
        self.long_window = long_window
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Takes the raw market data and calculates 2 moving averages and outputs when you have to buy and sell.
        """
        # Creates a copy to avoid affecting original data
        df = data.copy()

        # Calculates the short and long simple moving averages
        df['short_ma'] = df['close'].rolling(window=self.short_window).mean()
        df['long_ma'] = df['close'].rolling(window=self.long_window).mean()

        # Assume at the start that we do nothing
        df['signal'] = 0
        
        # If the short MA is larger than long then momentum is up so buy (1) and the opposite means sell (-1)
        df.loc[df['short_ma'] > df['long_ma'], 'signal'] = 1
        df.loc[df['short_ma'] < df['long_ma'], 'signal'] = -1

        return df