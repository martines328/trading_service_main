import time
from datetime import datetime

import config
from Strategy.control_position import ControlPosition
from client_service.client import Client_Manager
from client_service.client_future_action import Clietn_future_action
from data_frame_service.data_frame import Data_frame
from orders.orders_futures import Orders
from price_service import Price_service
from ta.ta_indicators import Indicators


class SuperTrend_Rsi_Strategy:

    def __init__(self):
        self.data_frame = Data_frame()
        self.price_service = Price_service()
        self.client = Client_Manager(config.api_key_real, config.api_secret_real, testnet=False)
        # self.client = Client_Manager(config.BINANCE_API_KEY_testnet, config.BINANCE_SECRET_KEY_testnet, testnet=True)
        self.future_action = Clietn_future_action()
        self.order = Orders()
        self.control_position = ControlPosition()

    def synchronize_startegy(self):
        binance_client = self.client.create_binance_client()
        print("***** Init trading configuration *****")
        print(f'Coin - {config.trading_symbol}, quantity - {config.position_quantity}')
        self.future_action.change_leverage(binance_client, config.trading_symbol, config.leverage)
        self.future_action.client_future_balance(binance_client)
        print(f'Trading interval - {config.trend_interval_1h}')
        binance_client.close_connection()

    def strategy_trading(self):
        print("Start trading 2H strategy")
        self.synchronize_startegy()

        super_trend_lenght = 10
        super_trend_multiplier = 3.0

        self.last_trade_time = 0

        while True:
            try:
                binance_client = self.client.create_binance_client()
                data_frame_1h = self.data_frame.get_data_frame(binance_client, config.trading_symbol,
                                                               config.trend_interval_1h, config.trend_start_time)

                data_frame_15m = self.data_frame.get_data_frame(binance_client, config.trading_symbol,
                                                                config.trend_interval_15m, config.trend_start_time)

                indicators_15m = Indicators(data_frame_15m)
                indicators = Indicators(data_frame_1h)

                if self.future_action.check_open_position_bool(binance_client, config.trading_symbol):
                    self.control_open_position(client=binance_client, data_frame=data_frame_1h, indicators=indicators, )
                    time.sleep(config.delayt_time_control_position - time.time() % config.delayt_time_control_position)
                    binance_client.close_connection()

                else:
                    self.order.cancel_all_open_orders(binance_client, config.trading_symbol)

                    binance_client.close_connection()

                    # current_time = time.time()
                    # # Перевірка на охолодження
                    # if current_time - self.last_trade_time < config.cooldown_period:
                    #     print("Cooldown active. Waiting to open new position...")
                    #     time.sleep(10)  # Очікуємо перед повторною перевіркою
                    #     continue

                    time.sleep(config.delayt_time - time.time() % config.delayt_time)

                    binance_client = self.client.create_binance_client()

                    # last_kline_price = self.data_frame.get_last_kline_price(data_frame)

                    #################### 1H indicators
                    rsi_1 = float(indicators.rsi(lenght=14, number=1, round_num=2))

                    ema50 = float(indicators.ema(lenght=50))
                    ema200 = float(indicators.ema(lenght=200))

                    atr = float(indicators.atr(lenght=14, number=1))
                    adx = float(indicators.adx_di(1))

                    super_trnd_1 = float(
                        indicators.supertrend(1, length=super_trend_lenght, multiplier=super_trend_multiplier,
                                              round_number=2))

                    ############### 15M indicators

                    super_trend_1_15m = float(
                        indicators_15m.supertrend(1, length=super_trend_lenght, multiplier=super_trend_multiplier,
                                                  round_number=2))

                    rsi_1_15m = float(indicators_15m.rsi(lenght=14, number=1, round_num=2))

                    adx_15m = float(indicators_15m.adx_di(1))

                    current_price = float(self.price_service.get_current_price(config.trading_symbol))

                    ### Trading logic
                    atr_threshold = 450  # значення можна змінювати залеєно від значення ціний
                    adx_threshold = 25

                    atr_signal = atr > atr_threshold
                    adx_signal = adx > adx_threshold
                    adx_filter = adx_15m > adx_threshold

                    ### long
                    if (atr_signal == True and adx_signal == True and current_price > ema50 > ema200
                            and rsi_1 < 70 and current_price > super_trnd_1 and current_price > super_trend_1_15m
                            and rsi_1_15m < 70 and adx_filter == True):
                        self.long_strsi_position(binance_client)
                        # self.set_stop_loss(self.client, current_price, atr, "long", config.round_num)
                        # self.last_trade_time = current_time  # Оновлення часу останньої угоди

                        continue
                    ###short
                    if (atr_signal == True and adx_signal == True and current_price < ema50 < ema200
                            and rsi_1 > 30 and current_price < super_trnd_1 and adx_filter == True and rsi_1_15m > 30
                            and current_price < super_trend_1_15m):
                        self.short_strsi_position(binance_client)
                        # self.set_stop_loss(self.client, current_price, atr, "short", config.round_num)
                        # self.last_trade_time = current_time  # Оновлення часу останньої угоди
                        continue


                    # if super_trnd_2 > last_kline_price and super_trnd_1 < current_price:
                    #     self.long_strsi_position(binance_client)
                    #     continue
                    # if super_trnd_2 < last_kline_price and super_trnd_1 > current_price:
                    #     self.short_strsi_position(binance_client)
                    #     continue

                    else:
                        current_time = datetime.now()
                        formatted_current_time = current_time.strftime("%m-%d %H:%M:%S")
                        print(
                            f"Waiting position {config.trading_symbol} {formatted_current_time}  current_price - {current_price} ")
                        with open('sprtrnd_rsi_log.txt', 'a') as f:
                            f.write(f"Waiting position {config.trading_symbol} {formatted_current_time}  ")

                binance_client.close_connection()

            except Exception as e:
                print("!!!!!!!!!!!!!!!!!!!ERROR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print(e)

    def short_strsi_position(self, client):
        position_order = self.order.placeSellOrder(client, config.trading_symbol, config.position_quantity)
        current_price = float(self.price_service.get_current_price(config.trading_symbol))
        # activation = current_price - (current_price * config.trailing_activation_percent / 100)
        # activation_price = round(float(activation), config.round_num)
        # # trailing = self.order.short_trailing_stop(client, config.trading_symbol, config.position_quantity,
        # #                                           activation_price, config.callback_rate)

        print('!!!!!!')
        print(
            f"{position_order['symbol']} || {position_order['side']} || {position_order['origQty']}"
            f" || {current_price}")
        # print(
        #     f"Trailing stop {trailing['symbol']} || Activate price {trailing['activatePrice']} "
        #     f"|| {trailing['priceRate']}")
        # print(position_order)
        print('!!!!!!')

    def long_strsi_position(self, client):
        position_order = self.order.placeBuyOrder(client, config.trading_symbol, config.position_quantity)
        current_price = float(self.price_service.get_current_price(config.trading_symbol))

        # activation = (current_price * config.trailing_activation_percent / 100) + current_price
        # activation_price = "{:.4f}".format(activation)
        # activation_price = round(float(activation), config.round_num)
        # trailing = self.order.long_trailing_stop(client, config.trading_symbol, config.position_quantity,
        #                                          activation_price, config.callback_rate)

        print('!!!!!!')
        print(
            f"{position_order['symbol']} || {position_order['side']} || {position_order['origQty']} "
            f"|| {current_price}")
        # print(
        #     f"Trailing stop {trailing['symbol']} || Activate price {trailing['activatePrice']} "
        #     f"|| {trailing['priceRate']}")

        print(f'LONG Trend {config.trading_symbol}, current price -  {current_price} $')
        print('!!!!!!')

    def control_open_position(self, **kwargs):
        client = kwargs['client']
        data_frame = kwargs['data_frame']

        indicators = kwargs['indicators']

        super_trend_lenght = 10
        super_trend_multiplier = 3.0

        rsi_hight_level: float = 70.0
        rsi_low_level: float = 30.0

        adx_threshold = 25

        trading_symbol = config.trading_symbol
        # trading_amount = config.position_quantity

        position_amount, entry_price, unrealized_profit = self.future_action.future_position_data(client,
                                                                                                  trading_symbol,
                                                                                                  config.round_num)
        current_price = float(self.price_service.get_current_price(config.trading_symbol))
        last_kline_price = self.data_frame.get_last_kline_price(data_frame)

        super_trnd_1 = float(
            indicators.supertrend(1, length=super_trend_lenght, multiplier=super_trend_multiplier, round_number=1))
        super_trnd_2 = float(
            indicators.supertrend(2, length=super_trend_lenght, multiplier=super_trend_multiplier, round_number=1))

        rsi_1 = float(indicators.rsi(lenght=14, number=1, round_num=2))
        rsi_2 = float(indicators.rsi(lenght=14, number=2, round_num=2))
        rsi_3 = float(indicators.rsi(lenght=14, number=3, round_num=2))

        adx = float(indicators.adx_di(1))

        # CLOSE POSITION WITH CHANGE SUPERTREND
        if position_amount > 0 and super_trnd_2 < last_kline_price and super_trnd_1 > current_price and super_trnd_1 > super_trnd_2:
            # close long change supertrend
            self.order.close_open_position_market(client, trading_symbol, position_amount)
            self.order.cancel_all_open_orders(client, trading_symbol)
        if position_amount < 0 and super_trnd_2 > last_kline_price and super_trnd_1 < current_price and super_trnd_1 < super_trnd_2:
            # close short change supertrend
            self.order.close_open_position_market(client, trading_symbol, position_amount)
            self.order.cancel_all_open_orders(client, trading_symbol)
        # CHANGE POS WITH RSI OVER
        if position_amount > 0 and rsi_1 < rsi_2 and rsi_3 < rsi_2 and rsi_2 > rsi_hight_level:
            # new trailing activation with curr percent DONE
            self.order.close_open_position_market(client, trading_symbol, position_amount)
            self.order.cancel_all_open_orders(client, trading_symbol)

        if position_amount < 0 and rsi_1 > rsi_2 and rsi_3 > rsi_2 and rsi_2 < rsi_low_level:
            self.order.close_open_position_market(client, trading_symbol, position_amount)
            self.order.cancel_all_open_orders(client, trading_symbol)

        if adx < adx_threshold:
            self.order.close_open_position_market(client, trading_symbol, position_amount)
            self.order.cancel_all_open_orders(client, trading_symbol)

        # current_time = datetime.now()
        # formatted_current_time = current_time.strftime("%m-%d %H:%M:")
        #     print(f"Control position {config.trading_symbol} {formatted_current_time} current_price - {current_price}"
        #           f" |  Position profit - {round(unrealized_profit, 5)}\n")
        #     with open('sprtrnd_rsi_log.txt', 'a') as f:
        #         f.write(f"Control position {config.trading_symbol} {formatted_current_time}")
        #         f.write(
        #             f"current_price - {current_price} | supertrend1 - {super_trnd_2} supertrend2 - {super_trnd_2}\n")
        #         f.write(f"Position profit ** {round(unrealized_profit, 5)}\n")

    def set_stop_loss(self, client, current_price, atr, position, round_num):
        """
        Встановлює стоп-лос залежно від ATR та типу позиції (long/short).
        """
        atr_multiplier = 3

        if position == "long":
            stop_loss_price = current_price - (atr * atr_multiplier)
        elif position == "short":
            stop_loss_price = current_price + (atr * atr_multiplier)
        else:
            return None

        stop_loss_price = round(stop_loss_price, round_num)

        # Виставлення стоп-лоса
        stop_loss_order = self.order.placeStopLossOrder(
            client, config.trading_symbol, config.position_quantity, stop_loss_price, position
        )
        print(f"Stop Loss Set at: {stop_loss_price} for {position}")
        return stop_loss_order

    def test_futures_orders(self):
        try:
            binance_client = self.client.create_binance_client()
            data_frame = self.data_frame.get_data_frame(binance_client, config.trading_symbol,
                                                        config.trend_interval_1h, config.trend_start_time)
            indicators = Indicators(data_frame)
            current_time = time.time()

            atr = float(indicators.atr(lenght=14, number=1))
            adx = float(indicators.adx_di(1))

            current_price = float(self.price_service.get_current_price(config.trading_symbol))

            ### Trading logic
            atr_threshold = 425  # значення можна змінювати залеєно від значення ціний
            adx_threshold = 25

            atr_signal = atr > atr_threshold
            adx_signal = adx > adx_threshold

            # self.long_strsi_position(binance_client)
            # self.set_stop_loss(self.client, current_price, atr, "long", config.round_num)
            self.last_trade_time = current_time

        except Exception as e:
            print(e)
