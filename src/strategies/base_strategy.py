import pandas as pd

class BaseStrategy:
    """
    Sets up a format for all future trading strategies to follow so they all have the same structure.
    """
    def init(self, name="Base Strategy"):
        """
        Naming the strategy.
        """
        self.name = name
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        This function looks at the prices and add a new column called 'signal'. 
        Signal rules:
         1 = Buy
        -1 = Sell / Short
         0 = Do nothing / Hold

         And raises an error such that real logic will need to be written in with specific strategies as no real logic is written here.
        """
        raise NotImplementedError("Every strategy must create its own generate_signals rules.")