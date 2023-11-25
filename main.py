import threading
import logging
from Strategy.ccistrategy import CciStrategy
from Strategy.macd_sprtrnd_strategy_2h import Macd_sprtrnd_strategy_2h
from Strategy.trendstrategy import TrendStrategy


def main():

    cci_strategy  = CciStrategy()
    trend_strategy = TrendStrategy()
    ts_macd_strategy = Macd_sprtrnd_strategy_2h()



    #thread1 = threading.Thread(target=cci_strategy.get_trend_data)
    #thread1.start()

    # thread2 = threading.Thread(target=trend_strategy.synchronize())
    # thread2.start()

    thread3 = threading.Thread(target=ts_macd_strategy.trade_strategy())
    thread3.start()
    logging.info("Start strategy thread")

if __name__ == "__main__":
    main()