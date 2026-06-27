import pandas as pd
import numpy as np

from src.base_strategy import BaseStrategy

class MovingAverageCrossStrategy(BaseStrategy):
    """
    A Trend-Following strategy. 
    It buys when a fast moving average crosses above a slow moving average.
    """
    def __init__(self, short_window=50, long_window=200, name="MA Crossover"):
        super().__init__(name)