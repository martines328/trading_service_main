import time
import logging
from datetime import datetime

import config
from client_service.client import Client_Manager
from client_service.client_future_action import Clietn_future_action
from data_frame_service.data_frame import Data_frame
from orders.orders_futures import Orders
from price_service import Price_service
from ta.ta_indicators import Indicators


class Macd_sprtrnd_strategy_2h:

    def __init__(self):
        self.data_frame = Data_frame()
        self.price_service = Price_service()
        self.client = Client_Manager(config.api_key_real, config.api_secret_real, testnet=False)
        # self.client = Client_Manager(config.BINANCE_API_KEY_testnet, config.BINANCE_SECRET_KEY_testnet, testnet=True)
        self.future_action = Clietn_future_action()
        self.order = Orders()

    def trade_strategy(self):
        print("Start trading 2H strategy")
        self.synchronize_startegy()

        macd_shortMA = 12
        macd_longMA = 21
        macd_signal = 9
        super_trend_lenght = 10
        super_trend_multiplier = 1.33
        mfi_lenght = 14
        logging.basicConfig(level=logging.INFO, filename="trading.log", filemode="w",
                            format="%(asctime)s %(levelname)s %(message)s")

        current_time = datetime.now()
        formatted_current_time = current_time.strftime("%m-%d %H:%M:")

        while True:
            try:
                binance_client = self.client.create_binance_client()
                data_frame = self.data_frame.get_data_frame(binance_client, config.ts_macd_symbol,
                                                            config.ts_macd_interval, config.ts_macd_interval_start_time)
                indicators = Indicators(data_frame)
                self.current_price = float(self.price_service.get_current_price(config.ts_macd_symbol))

                if self.future_action.check_open_position_bool(binance_client, config.ts_macd_symbol):
                    self.control_open_position(client=binance_client, data_frame=data_frame, indicators=indicators, )

                else:

                    self.order.cancel_all_open_orders(binance_client, config.ts_macd_symbol)
                    time.sleep(config.ts_macd_delay_time - time.time() % config.ts_macd_delay_time)

                    macd_line_1, signal_line_1 = indicators.macd(macd_shortMA, macd_longMA, macd_signal, 1, 1)
                    macd_line_2, signal_line_2 = indicators.macd(macd_shortMA, macd_longMA, macd_signal, 2, 2)
                    # macd_line_3, signal_line_3 = indicators.macd(macd_shortMA, macd_longMA, macd_signal, 3, 3)
                    super_trnd_1 = float(
                        indicators.supertrend(1, length=super_trend_lenght, multiplier=super_trend_multiplier,
                                              round_number=4))
                    super_trnd_2 = float(
                        indicators.supertrend(2, length=super_trend_lenght, multiplier=super_trend_multiplier,
                                              round_number=4))


                    if (macd_line_1 > signal_line_1 and macd_line_2 < signal_line_2
                            and super_trnd_1 < self.current_price):
                        self.long_macd_position(binance_client)

                    if (macd_line_1 < signal_line_1 and macd_line_2 > signal_line_2
                            and super_trnd_1 > self.current_price):
                        self.short_macd_position(binance_client)

                    if macd_line_1 > signal_line_1 and macd_line_2 > signal_line_2 and super_trnd_1 < self.current_price < super_trnd_2:
                        self.long_macd_position(binance_client)

                    if macd_line_1 < signal_line_1 and macd_line_2 < signal_line_2 and super_trnd_1 > self.current_price > super_trnd_2:
                        self.short_macd_position(binance_client)


                    with open('macd_sptrndl_log.txt', 'a') as f:
                        f.write(f"Witing position {config.ts_macd_symbol} {formatted_current_time}")
                        f.write(f"macd1 - {macd_line_1} signal1 - {signal_line_1} | macd2 - {macd_line_2} signal2 - {signal_line_2}"
                                f"current_price - {self.current_price} | supertrend1 - {super_trnd_2} supertrend1 - {super_trnd_2}\n")

                binance_client.close_connection()

            except Exception as e:
                print(e)

    def synchronize_startegy(self):
        binance_client = self.client.create_binance_client()
        print("***** Init trading configuration *****")
        print(f'Coin - {config.ts_macd_symbol}, quantity - {config.ts_macd_pos_amount}')
        self.future_action.change_leverage(binance_client, config.ts_macd_symbol, config.ts_macd_leverage)
        self.future_action.client_future_balance(binance_client)
        print(f'Trading interval - {config.ts_macd_interval}')
        binance_client.close_connection()

    def short_macd_position(self, client):
        position_order = self.order.placeSellOrder(client, config.ts_macd_symbol, config.ts_macd_pos_amount)
        current_price = float(self.price_service.get_current_price(config.ts_macd_symbol))
        activation = current_price - (current_price * config.ts_macd_trailing_activation_percent / 100)
        activation_price = round(float(activation), config.ts_macd_round)
        trailing = self.order.short_trailing_stop(client, config.ts_macd_symbol, config.ts_macd_pos_amount,
                                                  activation_price, config.ts_macd_callback_rate)
        logging.info("Create SHORT position ")
        logging.info(f"Entry price {current_price}  ")
        logging.info(f"Create Trailing stop with price {activation_price} ")
        print('!!!!!!')
        print(
            f"{position_order['symbol']} || {position_order['side']} || {position_order['origQty']}"
            f" || {current_price}")
        print(
            f"Trailing stop {trailing['symbol']} || Activate price {trailing['activatePrice']} "
            f"|| {trailing['priceRate']}")
        # print(position_order)
        print('!!!!!!')

    def long_macd_position(self, client):
        position_order = self.order.placeBuyOrder(client, config.ts_macd_symbol, config.ts_macd_pos_amount)
        current_price = float(self.price_service.get_current_price(config.ts_macd_symbol))
        activation = (current_price * config.ts_macd_trailing_activation_percent / 100) + current_price
        # activation_price = "{:.4f}".format(activation)
        activation_price = round(float(activation), config.ts_macd_round)
        trailing = self.order.long_trailing_stop(client, config.ts_macd_symbol, config.ts_macd_pos_amount,
                                                 activation_price, config.ts_macd_callback_rate)
        logging.info("Create LONG position ")
        logging.info(f"Entry price {current_price}  ")
        logging.info(f"Create Trailing stop with price {activation_price} ")
        print('!!!!!!')
        print(
            f"{position_order['symbol']} || {position_order['side']} || {position_order['origQty']} "
            f"|| {current_price}")
        print(
            f"Trailing stop {trailing['symbol']} || Activate price {trailing['activatePrice']} "
            f"|| {trailing['priceRate']}")

        print(f'LONG Trend {config.trading_symbol}, current price -  {self.current_price} $')
        print('!!!!!!')

    def control_open_position(self, **kwargs):

        macd_shortMA = 12
        macd_longMA = 21
        macd_signal = 9

        super_trend_lenght = 8
        super_trend_multiplier = 0.88
        trading_symbol = config.ts_macd_symbol  # maticusdt
        trading_amount = config.ts_macd_pos_amount  # 101

        time.sleep(config.ts_macd_position_delay_time - time.time() % config.ts_macd_position_delay_time)
        client = kwargs['client']
        # data_frame = kwargs['data_frame']

        indicators = kwargs['indicators']
        current_price = float(self.price_service.get_current_price(config.ts_macd_symbol))

        # data_frame = self.data_frame.get_data_frame(client, config.ts_macd_symbol,
        #                                            config.ts_macd_interval, config.ts_macd_interval_start_time)
        # indicators = Indicators(data_frame)

        super_trnd_1 = float(
            indicators.supertrend(1, length=super_trend_lenght, multiplier=super_trend_multiplier, round_number=4))
        super_trnd_2 = float(
            indicators.supertrend(2, length=super_trend_lenght, multiplier=super_trend_multiplier, round_number=4))
        macd_line_1, signal_line_1 = indicators.macd(macd_shortMA, macd_longMA, macd_signal, 1, 1)
        macd_line_2, signal_line_2 = indicators.macd(macd_shortMA, macd_longMA, macd_signal, 2, 2)
        # macd_line_3, signal_line_3 = indicators.macd(macd_shortMA, macd_longMA, macd_signal, 3, 3)

        position_amount, entry_price, unrealized_profit = self.future_action.future_position_data(client,
                                                                                                  trading_symbol,
                                                                                                  config.ts_macd_round)
        # self.control_trailing_callback(unrealized_profit=unrealized_profit, position_amount=position_amount,
        #                                client=client,
        #                                new_callBack_rate=2.5, trading_symbol=trading_symbol)

        if macd_line_2 > signal_line_2 and (macd_line_1 < signal_line_1 or macd_line_1 == signal_line_1)and position_amount > 0:
            # close long change macd
            self.order.close_open_position_market(client, trading_symbol, position_amount)
            self.order.cancel_all_open_orders(client, trading_symbol)

        elif macd_line_2 < signal_line_2 and (macd_line_1 > signal_line_1 or macd_line_1 == signal_line_1) and position_amount<0:
            # close short change macd
            self.order.close_open_position_market(client, trading_symbol, position_amount)
            self.order.cancel_all_open_orders(client, trading_symbol)

        elif macd_line_2 < signal_line_2 and macd_line_1 < signal_line_1 and super_trnd_2 > current_price > super_trnd_1 and position_amount <0:
            # close short change supertrend
            self.order.close_open_position_market(client, trading_symbol, position_amount)
            self.order.cancel_all_open_orders(client, trading_symbol)
        elif macd_line_2 > signal_line_2 and macd_line_1 > signal_line_1 and super_trnd_2 < current_price < super_trnd_1 and position_amount>0:
            # close long change supertrenf
            self.order.close_open_position_market(client, trading_symbol, position_amount)
            self.order.cancel_all_open_orders(client, trading_symbol)



        current_time = datetime.now()
        formatted_current_time = current_time.strftime("%m-%d %H:%M:")
        with open('macd_sptrndl_log.txt', 'a') as f:
            f.write(f"Control position {config.ts_macd_symbol} {formatted_current_time}")
            f.write(f"macd1 - {macd_line_1} signal1 - {signal_line_1} | macd2 - {macd_line_2} signal2 - {signal_line_2}"
                    f"current_price - {self.current_price} | supertrend1 - {super_trnd_2} supertrend1 - {super_trnd_2}\n")
            f.write( f"Position profit - {round(unrealized_profit,5)}\n")

    # def control_trailing_callback(self, **kwargs):  # doesn't work wiyh crossed
    #     unrealized_profit = float(kwargs['unrealized_profit'])
    #     position_amount = float(kwargs['position_amount'])
    #     client = kwargs['client']
    #     new_callBack_rate = float(kwargs['new_callBack_rate'])
    #     trading_symbol = kwargs['trading_symbol']
    #
    #     futures_action = Clietn_future_action()
    #
    #     if unrealized_profit > 3:
    #         futures_action.change_position_margin_type(client, trading_symbol, "ISOLATED")
    #         futures_action.change_position_margin(client, trading_symbol, position_amount, new_callBack_rate)
    #         futures_action.change_position_margin_type(client, trading_symbol, "CROSSED")
    #
    #
