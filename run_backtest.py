from backtest import Backtest

def main():
    symbol = '000001.SZ'
    start_date = '20200101'
    end_date = '20241231'
    short_window = 5
    long_window = 20

    backtest = Backtest()
    data = backtest.get_historical_data(symbol, start_date, end_date)
    result = backtest.run_backtest(data, short_window, long_window)
    # backtest.plot_results(result)
    backtest.plot_monthly_net_profit_loss(result)

if __name__ == "__main__":
    main()
