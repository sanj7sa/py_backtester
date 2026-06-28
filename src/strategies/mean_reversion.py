import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy

class BollingerMeanReversionStrategy(BaseStrategy):
    """
    Buy when the price drops below the bottom band and sell when spikes above the top band.
    """
    def __init__(self, window=20, num_std_dev=2, name="Bollinger Mean Reversion"):
        super().__init__(name)
        # Standardised parameters for Bollinger bands - 20 day average, 2 standard deviations
        self.window = window
        self.num_std_dev = num_std_dev

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()

        # Calculate the Simple moving average
        df['sma'] = df['close'].rolling(window=self.window).mean()

        # Calculate the standard deviation
        df['std_dev'] = df['close'].rolling(window=self.window).std()

        # Calculate the Rubber Bands (Upper and Lower limits)
        df['upper_band'] = df['sma'] + (df['std_dev'] * self.num_std_dev)
        df['lower_band'] = df['sma'] - (df['std_dev'] * self.num_std_dev)

        # Assumes the signal starts at 0
        df['signal'] = 0

        # Rules for the strategy
        df.loc[df['close'] < df['lower_band'], 'signal'] = 1
        df.loc[df['close'] > df['upper_band'], 'signal'] = -1

        return df
        