
from vnpy.app.cta_strategy import CtaTemplate, BarData, ArrayManager
from vnpy.trader.object import TradeData, OrderData
from vnpy.trader.constant import Interval
from vnpy.trader.engine import MainEngine, CtaEngine
from vnpy.trader.setting import SETTINGS
from vnpy.trader.utility import load_json, save_json

class DualMovingAverageStrategy(CtaTemplate):
    author = "GitHub Copilot"

    short_window = 10
    long_window = 20

    short_mavg = 0.0
    long_mavg = 0.0

    parameters = ["short_window", "long_window"]
    variables = ["short_mavg", "long_mavg"]

    def __init__(self, cta_engine: CtaEngine, strategy_name: str, vt_symbol: str, setting: dict):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.am = ArrayManager()

    def on_init(self):
        self.write_log("Strategy initialized")
        self.load_bar(10)

    def on_start(self):
        self.write_log("Strategy started")
        self.put_event()

    def on_stop(self):
        self.write_log("Strategy stopped")
        self.put_event()

    def on_tick(self, tick):
        pass

    def on_bar(self, bar: BarData):
        self.am.update_bar(bar)
        if not self.am.inited:
            return

        self.short_mavg = self.am.sma(self.short_window, array=True)[-1]
        self.long_mavg = self.am.sma(self.long_window, array=True)[-1]

        if self.short_mavg > self.long_mavg:
            if self.pos == 0:
                self.buy(bar.close_price, 1)
            elif self.pos < 0:
                self.cover(bar.close_price, 1)
                self.buy(bar.close_price, 1)
        elif self.short_mavg < self.long_mavg:
            if self.pos == 0:
                self.short(bar.close_price, 1)
            elif self.pos > 0:
                self.sell(bar.close_price, 1)
                self.short(bar.close_price, 1)

        self.put_event()

    def on_order(self, order: OrderData):
        pass

    def on_trade(self, trade: TradeData):
        self.put_event()

if __name__ == "__main__":
    SETTINGS["log.active"] = True
    SETTINGS["log.level"] = "INFO"
    SETTINGS["log.console"] = True

    main_engine = MainEngine()
    cta_engine = main_engine.add_app(CtaEngine)

    strategy_setting = {
        "class_name": "DualMovingAverageStrategy",
        "vt_symbol": "AAPL",
        "setting": {
            "short_window": 10,
            "long_window": 20
        }
    }

    cta_engine.init_engine()
    cta_engine.add_strategy(strategy_setting)
    cta_engine.init_all_strategies()
    cta_engine.start_all_strategies()