import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties

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
        font = FontProperties(fname='C:/Windows/Fonts/simsun.ttc')  # Path to a Chinese font file
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.plot(data.index, data['close'], label='收盘价')
        ax.plot(data.index, data['short_mavg'], label='短期均线')
        ax.plot(data.index, data['long_mavg'], label='长期均线')
        ax.plot(data[data['positions'] == 1].index, data['short_mavg'][data['positions'] == 1], '^', markersize=10, color='g', lw=0, label='买入信号')
        ax.plot(data[data['positions'] == -1].index, data['short_mavg'][data['positions'] == -1], 'v', markersize=10, color='r', lw=0, label='卖出信号')
        ax.set_title('双均线策略回测', fontproperties=font)
        ax.set_xlabel('日期', fontproperties=font)
        ax.set_ylabel('价格', fontproperties=font)
        ax.legend(prop=font)
        
        # Print the number of transactions on the subplot
        num_transactions = self.count_transactions(data)
        ax.text(0.02, 0.95, f'交易次数: {num_transactions}', transform=ax.transAxes, fontsize=12, verticalalignment='top', fontproperties=font)

        plt.show()

    def plot_net_profit_loss(self, data: pd.DataFrame, frequency: str, title: str):
        """
        Plot the net profit/loss based on the given frequency.
        """
        font = FontProperties(fname='C:/Windows/Fonts/simsun.ttc')  # Path to a Chinese font file
        net_profit_loss = data['cumulative_net_profit_loss'].resample(frequency).sum()
        fig, ax = plt.subplots(figsize=(12, 8))
        net_profit_loss.plot(kind='bar', ax=ax)
        ax.set_title(title, fontproperties=font)
        ax.set_xlabel('时间', fontproperties=font)
        ax.set_ylabel('净盈亏', fontproperties=font)
        ax.set_xticklabels([x.strftime('%Y-%m') for x in net_profit_loss.index], rotation=45, fontproperties=font)
        plt.show()

    def plot_quarterly_net_profit_loss(self, data: pd.DataFrame):
        """
        Plot the net profit/loss every 3 months.
        """
        self.plot_net_profit_loss(data, '3M', '季度净盈亏')

    def count_transactions(self, data: pd.DataFrame) -> int:
        """
        Count the number of transactions.
        """
        return data['positions'].abs().sum()
