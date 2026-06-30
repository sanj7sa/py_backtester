import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from data_loader import DataLoader
from strategies.moving_average import MovingAverageCrossStrategy
from strategies.mean_reversion import BollingerMeanReversionStrategy

TRADING_DAYS_PER_YEAR = 252

class Backtester:
    """
    This takes a dataset and a strategy, simulates the trades over time, calculates the performace and creates a visual report.
    """

    def __init__(self, data: pd.DataFrame, strategy, initial_capital=10000.0):
        self.data = data.copy()
        self.strategy = strategy
        self.initial_capital = initial_capital

    def run(self):
        """
        Runs the simulation step-by-step.
        """
        print(f"Running backtest for: {self.strategy.name}")

        # Analyse the data and generate the signal with data 
        self.data = self.strategy.generate_signals(self.data)
        # Calculates the daily percentage change of stock
        self.data['market_returns'] = self.data['close'].pct_change()
        # Makes a rule that uses .shift(1) to avoid Lookahead bias
        self.data['strategy_returns'] = self.data['signal'].shift(1) * self.data['market_returns']
        # Calculates the Portfolio value with cunmulative production
        self.data['portfolio_value'] = self.initial_capital * (1 + self.data['strategy_returns']).cumprod()
        # Calculates what would have happened if we buy and hold
        self.data['buy_and_hold_value'] = self.initial_capital * (1 + self.data['market_returns']).cumprod()

        # Cleans up the empty rows at the start of the data set
        self.data.dropna(inplace=True)

    def evaluate(self):
        """
        Calculates the performance metrics such as returns and Sharpe rati.
        """
        # Calculates the total return
        final_value = self.data['portfolio_value'].iloc[-1]
        total_return = ((final_value - self.initial_capital) / self.initial_capital) * 100

        buy_and_hold_final = self.data['buy_and_hold_value'].iloc[-1]
        buy_and_hold_return = ((buy_and_hold_final - self.initial_capital) / self.initial_capital) * 100

        # Calculates Sharpe ratio
        daily_returns = self.data['strategy_returns']
        if daily_returns.std() != 0:
            sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(TRADING_DAYS_PER_YEAR)
        else:
            sharpe_ratio = 0.0 
        
        print("\n" + "="*40)
        print(f"### STRATEGY REPORT: {self.strategy.name} ###")
        print("="*40)
        print(f"Initial Capital:    ${self.initial_capital:,.2f}")
        print(f"Final Value:        ${final_value:,.2f}")
        print(f"Total Return:       {total_return:.2f}%")
        print(f"Buy & Hold Return:  {buy_and_hold_return:.2f}%")
        print(f"Sharpe Ratio:       {sharpe_ratio:.2f} (Target > 1.0 is good)")
        print("="*40 + "\n")
    
    def plot(self):
        """
        Draws a graph that compares strategy to holding the stock.
        """
        plt.figure(figsize=(12,6))
        plt.plot(self.data.index, self.data['portfolio_value'], label=f"{self.strategy.name} Portfolio", color = "blue")
        plt.plot(self.data.index, self.data['buy_and_hold_value'], label='Buy & Hold Baseline', color='gray', linestyle='--')
        plt.title(f"Backtest Results: {self.strategy.name}")
        plt.xlabel("Date")
        plt.ylabel("Portfolio Value ($)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

if __name__ == "__main__":
    loader = DataLoader()
    aapl_data = loader.load_data("AAPL", start_date="2020-01-01", end_date="2024-12-31")

    if aapl_data is not None:

        ma_strategy = MovingAverageCrossStrategy(short_window=50, long_window=200)
        
        backtester = Backtester(data=aapl_data, strategy=ma_strategy, initial_capital=10000)
        
        backtester.run()
        backtester.evaluate()
        backtester.plot()