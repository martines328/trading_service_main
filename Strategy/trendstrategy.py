import threading
import time

import config
from client_service.client import Client_Manager
from client_service.client_future_action import Clietn_future_action
from data_frame_service.data_frame import Data_frame
from orders.orders_futures import Orders
from price_service import Price_service
from ta.ta_indicators import Indicators


class TrendStrategy:
    def __init__(self):
        self.data_frame = Data_frame()
        self.price_service = Price_service()
        # self.client = Client_Manager(config.api_key_real, config.api_secret_real, testnet=False)
        self.client = Client_Manager(config.BINANCE_API_KEY_testnet, config.BINANCE_SECRET_KEY_testnet, testnet=True)
        self.future_action = Clietn_future_action()

    def buy_trend_strategy(self, client):
        position = self.checkOpenPosition(client)
        order = Orders()
        if position == 1:
            print("You have open orders already")
            return
        if position == 0:
            print("buy")
            position_order = order.placeBuyOrder(client, config.ts_symbol, config.ts_pos_amount)
            current_price = float(self.price_service.get_current_price(config.ts_symbol))
            activation = (current_price * config.ts_trailing_activation_percent / 100) + current_price
            activation_price = "{:.1f}".format(activation)
            trailing = order.long_trailing_stop(client, config.ts_symbol, config.ts_pos_amount,
                                                activation_price, config.ts_callback_rate)
            print('!!!!!!')
            print(
                f"{position_order['symbol']} || {position_order['side']} || {position_order['origQty']} "
                f"|| {current_price}")
            print(
                f"Trailing stop {trailing['symbol']} || Activate price {trailing['activatePrice']} "
                f"|| {trailing['priceRate']}")

    def sell_trend_strategy(self, client):
        position = self.checkOpenPosition(client)
        order = Orders()
        if position == 1:
            print("You have open orders already")
            return
        if position == 0:
            print("sell")
            position_order = order.placeSellOrder(client, config.ts_symbol, config.ts_pos_amount)
            current_price = float(self.price_service.get_current_price(config.ts_symbol))
            activation = current_price - (current_price * config.ts_trailing_activation_percent / 100)
            activation_price = "{:.1f}".format(activation)
            trailing = order.short_trailing_stop(client, config.ts_symbol, config.ts_pos_amount,
                                                 activation_price, config.ts_callback_rate)
            print('!!!!!!')
            print(
                f"{position_order['symbol']} || {position_order['side']} || {position_order['origQty']}"
                f" || {current_price}")
            print(
                f"Trailing stop {trailing['symbol']} || Activate price {trailing['activatePrice']} "
                f"|| {trailing['priceRate']}")

            print('!!!!!!')

    def checkOpenPosition(self, client):
        pos = client.futures_position_information()
        for n in pos:
            if n['symbol'] == config.ts_symbol:
                position_amt = float(n['positionAmt'])
                if position_amt:
                    return 1
                else:
                    return 0

    def manageOpenPosition(self):
        while True:
            try:
                time.sleep(config.ts_manage_delayt_time - time.time() % config.ts_manage_delayt_time)
                binance_client = self.client.create_binance_client()

                pos = binance_client.futures_position_information()

                for n in pos:
                    if n['symbol'] == config.ts_symbol:
                        position_amt = float(n['positionAmt'])
                        if position_amt:
                            data_frame = self.data_frame.get_data_frame(binance_client, config.ts_symbol,
                                                                        config.ts_manage_pos_interval,
                                                                        config.ts_manage_start_time)
                            orders = Orders()
                            indicators = Indicators(data_frame)

                            current_price = float(self.price_service.get_current_price(config.trading_symbol))
                            super_trend = float(indicators.supertrend(1, length=10, multiplier=0.88))

                            # TODO
                            if position_amt > 0:  # long
                                if super_trend > current_price:
                                    cancel_orders = orders.cancel_all_open_orders(binance_client, config.trading_symbol)
                                    close_long_orders = orders.close_long(binance_client, config.trading_symbol,
                                                                          current_price)
                                    return

                            if position_amt < 0:  # short
                                if super_trend < current_price:
                                    cancel_orders = orders.cancel_all_open_orders(binance_client, config.trading_symbol)
                                    close_long_orders = orders.close_short(binance_client, config.trading_symbol, current_price)
                                    return

            except Exception as e:
                print(e)

    def get_ts_trend_data(self):
        print("Start trend trading")
        while True:
            try:
                time.sleep(config.ts_delay_time - time.time() % config.ts_delay_time)
                binance_client = self.client.create_binance_client()
                data_frame = self.data_frame.get_data_frame(binance_client, config.ts_symbol,
                                                            config.ts_trend_interval,
                                                            config.ts_trend_start_time)
                indicators = Indicators(data_frame)

                manage_pos_thread = threading.Thread(target=self.manageOpenPosition,
                                                     args=(binance_client, data_frame))
                manage_pos_thread.start()

                stc1, stc2, stc3, stc4 = float(indicators.stc(1)), float(indicators.stc(2)), float(
                    indicators.stc(3)), float(indicators.stc(4))
                current_price = float(self.price_service.get_current_price(config.ts_symbol))
                super_trend = float(indicators.supertrend(1, length=10, multiplier=0.88))

                cci1, cci2 = float(indicators.cci_trend(1)), float(indicators.cci_trend(2))
                if (stc1 > stc2 and stc1 > 10) and (
                        (stc2 and stc3 and stc4 in range(0, 3)) or (
                        (stc3 > stc2) and (stc2 and stc3 in range(0, 3)))):  # cause stc2 and stc3 might be 0.0
                    if current_price > super_trend and cci2 < cci1:
                        # buy signal
                        #     self.buy_trend_strategy(binance_client)
                        continue
                if (stc1 < stc2 and stc1 < 90) and (
                        (stc2 and stc3 and stc4 in range(98, 101)) or (
                        (stc3 < stc2) and (stc2 and stc3 in range(98, 101)))):
                    if current_price < super_trend and cci2 > cci1:
                        # sell signal
                        # self.sell_trend_strategy(binance_client)
                        continue
                else:
                    print("Wait trend")
                    continue
            except Exception as e:
                print(e)

    # TODO
    def synchronize(self):
        self.get_ts_trend_data()
        # manage_pos_thread = threading.Thread(target=self.manageOpenPosition,args=())
        # manage_pos_thread.start()
