import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class Backtest:
    def get_historical_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch historical data from Tushare.
        """
        ts.set_token('9e64f47aa6b67e810e4b3defb3200e640f36c3fffeeb5149d73293c7')
        pro = ts.pro_api()
        df = pro.daily(ts_code=symbol, start_date=start_date, end_date=end_date)
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df.set_index('trade_date', inplace=True)
        df.sort_index(inplace=True)
        return df

    def run_backtest(self, data: pd.DataFrame, short_window: int, long_window: int) -> pd.DataFrame:
        """
        Execute a dual moving average backtest.
        """
        data['short_mavg'] = data['close'].rolling(window=short_window, min_periods=1).mean()
        data['long_mavg'] = data['close'].rolling(window=long_window, min_periods=1).mean()
        data['signal'] = 0
        data.iloc[short_window:, data.columns.get_loc('signal')] = np.where(data['short_mavg'].iloc[short_window:] > data['long_mavg'].iloc[short_window:], 1, 0)
        data['positions'] = data['signal'].diff()

        # Calculate transaction fees and net profit/loss
        data['transaction_fee'] = 0
        data['net_profit_loss'] = 0
        data['cumulative_net_profit_loss'] = 0
        shares = 20000
        fee_rate = 0.0003

        data = data.reset_index()  # Reset index to use positional indexing

        for i in range(1, len(data)):
            if data['positions'].iloc[i] != 0:
                data.loc[i, 'transaction_fee'] = shares * data.loc[i, 'close'] * fee_rate
            data.loc[i, 'net_profit_loss'] = (data.loc[i, 'close'] - data.loc[i-1, 'close']) * shares - data.loc[i, 'transaction_fee']
            data.loc[i, 'cumulative_net_profit_loss'] = data.loc[i-1, 'cumulative_net_profit_loss'] + data.loc[i, 'net_profit_loss']

        data = data.set_index('trade_date')  # Set index back to 'trade_date'

        return data

    def plot_results(self, data: pd.DataFrame):
        """
        Plot the backtest results.
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.plot(data.index, data['close'], label='Close Price')
        ax.plot(data.index, data['short_mavg'], label='Short Moving Average')
        ax.plot(data.index, data['long_mavg'], label='Long Moving Average')
        ax.plot(data[data['positions'] == 1].index, data['short_mavg'][data['positions'] == 1], '^', markersize=10, color='g', lw=0, label='Buy Signal')
        ax.plot(data[data['positions'] == -1].index, data['short_mavg'][data['positions'] == -1], 'v', markersize=10, color='r', lw=0, label='Sell Signal')
        ax.set_title('Dual Moving Average Strategy Backtest')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.legend()
        plt.show()

    def plot_monthly_net_profit_loss(self, data: pd.DataFrame):
        """
        Plot the net profit/loss every 3 months.
        """
        quarterly_net_profit_loss = data['cumulative_net_profit_loss'].resample('3ME').sum()
        fig, ax = plt.subplots(figsize=(12, 8))
        quarterly_net_profit_loss.plot(kind='bar', ax=ax)
        ax.set_title('Quarterly Net Profit/Loss')
        ax.set_xlabel('Quarter')
        ax.set_ylabel('Net Profit/Loss')
        ax.set_xticklabels([x.strftime('%Y-%m') for x in quarterly_net_profit_loss.index], rotation=45)
        plt.show()
