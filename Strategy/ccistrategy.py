import threading
import time
from datetime import datetime

import config
from client_service.client import Client_Manager
from client_service.client_future_action import Clietn_future_action
from data_frame_service.data_frame import Data_frame
from orders.orders_futures import Orders
from price_service import Price_service
from ta.ta_indicators import Indicators


class CciStrategy:
    def __init__(self):
        self.data_frame = Data_frame()
        self.price_service = Price_service()
        self.client = Client_Manager(config.api_key_real, config.api_secret_real, testnet=False)
        # self.client = Client_Manager(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY, testnet=True)
        self.future_action = Clietn_future_action()

    def cci_sell_trend_strategy(self, client):
        try:
            data_frame = self.data_frame.get_data_frame(client, config.trading_symbol, config.interval,
                                                        config.start_time)
            indicator = Indicators(data_frame)
            order = Orders()

            cci1, cci2, cci3 = indicator.cci_trend(number=1), indicator.cci_trend(number=2), indicator.cci_trend(
                number=3)



            if cci1 < cci2 and int(cci1) in range(150, 500) and int(cci2) in range(230, 500):
                if cci3 < cci2 and int(cci3) in range(150, 500):
                    print("cci sell")
                    position_order = order.placeSellOrder(client, config.trading_symbol, config.position_quantity)
                    current_price = float(self.price_service.get_current_price(config.trading_symbol))
                    activation = current_price - (current_price * config.trailing_activation_percent / 100)
                    activation_price = "{:.1f}".format(activation)
                    trailing = order.short_trailing_stop(client, config.trading_symbol, config.position_quantity,
                                                         activation_price, config.callback_rate)
                    print('!!!!!!')
                    print(
                        f"{position_order['symbol']} || {position_order['side']} || {position_order['origQty']}"
                        f" || {current_price}")
                    print(
                        f"Trailing stop {trailing['symbol']} || Activate price {trailing['activatePrice']} "
                        f"|| {trailing['priceRate']}")
                    # print(position_order)
                    print('!!!!!!')
                    # print(trailing)
            with open('cci.txt', 'a+') as f:
                f.write(str(f'{cci3}   {cci2}   {cci1} \n'))
            print(f'SHORT Trend {config.trading_symbol}, current price -  {self.current_price} $')
        except Exception as e:
            print(e)

    #
    #
    # def teststartegy(self ):
    #     binance_client = self.client.create_binance_client()
    #     data_frame = self.data_frame.get_data_frame(binance_client, config.trading_symbol,
    #                                                 config.trend_interval,
    #                                                 config.trend_start_time)
    #
    #     df_clode = data_frame['close']
    #     for n in data_frame:


    @staticmethod
    def check_position(client, macd, signal):
        try:
            pos = client.futures_position_information()
            orders = Orders()

            close_level: float = 20.2

            for n in pos:
                if n['symbol'] == config.trading_symbol:
                    # print(n)
                    entry_price = round(float(n['entryPrice']), 2)
                    position_amt = float(n['positionAmt'])
                    # TODO
                    unRealizedProfit = float(n['unRealizedProfit'])
                    if position_amt:
                        if position_amt > 0.0:
                            if macd < signal or macd - signal < close_level:
                                print("Close LONG position")
                                long_close_price = entry_price + 20
                                cancel_orders = orders.cancel_all_open_orders(client, config.trading_symbol)
                                close_long_orders = orders.close_long(client, config.trading_symbol, long_close_price)
                                return
                #TODO трайлінг стоп процентовкою у відкритій позиції від профіта
                        if position_amt < 0.0:
                            if macd > signal or macd - signal > - close_level:
                                print("Close SHORT position")
                                position_amt = abs(position_amt)
                                short_close_price = entry_price - 20
                                cancel_orders = orders.cancel_all_open_orders(client, config.trading_symbol)
                                close_long_orders = orders.close_short(client, config.trading_symbol, short_close_price)
                                return

                    else:
                        orders.cancel_all_open_orders(client, config.trading_symbol)
        except Exception as e:
            print(e)

    def cci_buy_trend_strategy(self, client):
        try:
            data_frame = self.data_frame.get_data_frame(client, config.trading_symbol, config.interval,
                                                        config.start_time)
            indicator = Indicators(data_frame)
            order = Orders()

            cci1, cci2, cci3 = indicator.cci_trend(number=1), indicator.cci_trend(number=2), indicator.cci_trend(
                number=3)

            with open('cci.txt', 'a+') as f:
                f.write(str(f'{cci3}   {cci2}   {cci1} \n'))

            if cci1 > cci2 and int(cci1) in range(-500, -150) and int(cci2) in range(-500, -200):
                if cci3 > cci2 and int(cci3) in range(-500, -150):
                    # init buy pos
                    print('cci buy')
                    position_order = order.placeBuyOrder(client, config.trading_symbol, config.position_quantity)
                    current_price = float(self.price_service.get_current_price(config.trading_symbol))
                    activation = (current_price * config.trailing_activation_percent / 100) + current_price
                    activation_price = "{:.1f}".format(activation)
                    trailing = order.long_trailing_stop(client, config.trading_symbol, config.position_quantity,
                                                        activation_price, config.callback_rate)
                    print('!!!!!!')
                    print(
                        f"{position_order['symbol']} || {position_order['side']} || {position_order['origQty']} "
                        f"|| {current_price}")
                    print(
                        f"Trailing stop {trailing['symbol']} || Activate price {trailing['activatePrice']} "
                        f"|| {trailing['priceRate']}")
            print(f'LONG Trend {config.trading_symbol}, current price -  {self.current_price} $')
            print('!!!!!!')
        except Exception as e:
            print(e)

    def get_trend_data(self):
        print("Start traiding")
        self.synchronize()
        while True:
            try:
                time.sleep(config.delayt_time - time.time() % config.delayt_time)
                binance_client = self.client.create_binance_client()
                data_frame = self.data_frame.get_data_frame(binance_client, config.trading_symbol,
                                                            config.trend_interval,
                                                            config.trend_start_time)
                indicators = Indicators(data_frame)

                macd_line, signal_line = indicators.macd(19, 39, 9)
                self.current_price = float(self.price_service.get_current_price(config.trading_symbol))
                super_trnd = float(indicators.supertrend(1, length=10, multiplier=3.0))

                check_pos_thread = threading.Thread(target=self.check_position,
                                                    args=(binance_client, macd_line, signal_line))
                check_pos_thread.start()

                current_time = datetime.now()
                formatted_current_time = current_time.strftime("%m-%d %H:%M:")


                if macd_line > signal_line and super_trnd < self.current_price:
                    self.cci_buy_trend_strategy(binance_client)
                    continue
                if macd_line < signal_line and super_trnd > self.current_price:
                    # if  macd_line - signal_line > - close_level:
                    self.cci_sell_trend_strategy(binance_client)
                    continue
                else:
                    print("***********")
                    print(f"Waiting trend  {formatted_current_time}")
                    print(f"MACD - {macd_line}, signal - {signal_line}, supertrend - {super_trnd}, current price { self.current_price}")
                    continue
            except Exception as e:
                print(e)

    def synchronize(self):
        binance_client = self.client.create_binance_client()

        print("Init trading configuration")
        print(f'coin - {config.trading_symbol}, quantity - {config.position_quantity}')
        self.future_action.change_leverage(binance_client, config.trading_symbol, config.leverage)
        self.future_action.client_future_balance(binance_client)
        binance_client.close_connection()
