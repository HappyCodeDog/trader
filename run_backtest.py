from backtest import Backtest
import matplotlib.pyplot as plt

def main():
    symbol = '300059.SZ'
    start_date = '20200101'
    end_date = '20241231'
    short_window = 5
    long_window = 20

    backtest = Backtest()
    data = backtest.get_historical_data(symbol, start_date, end_date)
    result = backtest.run_backtest(data, short_window, long_window)
    num_transactions = backtest.count_transactions(result)
    print(f"Number of transactions: {num_transactions}")
    backtest.plot_results(result)
    plt.show(block=False)
    plt.pause(0.001)
    backtest.plot_quarterly_net_profit_loss(result)
    plt.show()

if __name__ == "__main__":
    main()
