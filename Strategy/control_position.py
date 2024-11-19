import time
from datetime import datetime

import config
from client_service.client_future_action import Clietn_future_action
from orders.orders_futures import Orders
from price_service import Price_service


class ControlPosition:

    def __init__(self):
        self.price_service = Price_service()
        self.future_action = Clietn_future_action()
        self.order = Orders()

    def control_close_position(self, **kwargs):

        time.sleep(config.ts_macd_position_delay_time - time.time() % config.ts_macd_position_delay_time)

        macd_shortMA = 12
        macd_longMA = 21
        macd_signal = 9

        super_trend_lenght = 8
        super_trend_multiplier = 0.88

        trading_symbol = config.ts_macd_symbol  # maticusdt
        trading_amount = config.ts_macd_pos_amount  # 101

        indicators = kwargs['indicators']
        data_frame = kwargs['data_frame']
        client = kwargs["client"]

        position_amount, entry_price, unrealized_profit = self.future_action.future_position_data(client,
                                                                                                  trading_symbol,
                                                                                                  config.ts_macd_round)

        current_price = float(self.price_service.get_current_price(config.ts_macd_symbol))

        super_trnd_1 = float(
            indicators.supertrend(1, length=super_trend_lenght, multiplier=super_trend_multiplier, round_number=4))
        super_trnd_2 = float(
            indicators.supertrend(2, length=super_trend_lenght, multiplier=super_trend_multiplier, round_number=4))
        macd_line_1, signal_line_1 = indicators.macd(macd_shortMA, macd_longMA, macd_signal, 1, 1)
        macd_line_2, signal_line_2 = indicators.macd(macd_shortMA, macd_longMA, macd_signal, 2, 2)
        # macd_line_3, signal_line_3 = indicators.macd(macd_shortMA, macd_longMA, macd_signal, 3, 3)

        if macd_line_2 > signal_line_2 and (
                macd_line_1 < signal_line_1 or macd_line_1 == signal_line_1) and position_amount > 0:
            # close long change macd
            self.order.close_open_position_market(client, trading_symbol, position_amount)
            self.order.cancel_all_open_orders(client, trading_symbol)

        elif macd_line_2 < signal_line_2 and (
                macd_line_1 > signal_line_1 or macd_line_1 == signal_line_1) and position_amount < 0:
            # close short change macd
            self.order.close_open_position_market(client, trading_symbol, position_amount)
            self.order.cancel_all_open_orders(client, trading_symbol)

        elif super_trnd_2 > current_price > super_trnd_1 and position_amount < 0:
            # close short change supertrend
            self.order.close_open_position_market(client, trading_symbol, position_amount)
            self.order.cancel_all_open_orders(client, trading_symbol)
            print("close short position at control ")
        elif super_trnd_2 < current_price < super_trnd_1 and position_amount > 0:
            # close long change supertrenf
            self.order.close_open_position_market(client, trading_symbol, position_amount)
            self.order.cancel_all_open_orders(client, trading_symbol)
            print("close long position at control ")

        # close position when indicator

        current_time = datetime.now()
        formatted_current_time = current_time.strftime("%m-%d %H:%M:")
        print(f"Control position {config.ts_macd_symbol} {formatted_current_time} current_price - {current_price}"
              f" |  Position profit - {round(unrealized_profit, 5)}\n")
        with open('macd_sptrndl_log.txt', 'a') as f:
            f.write(f"Control position {config.ts_macd_symbol} {formatted_current_time}")
            f.write(
                f"macd1 - {macd_line_1} signal1 - {signal_line_1} | macd2 - {macd_line_2} signal2 - {signal_line_2}"
                f"current_price - {current_price} | supertrend1 - {super_trnd_2} supertrend2 - {super_trnd_2}\n")
            f.write(f"Position profit - {round(unrealized_profit, 5)}\n")



    def control_trailing_callback(self, **kwargs):
        while True:
            try:
                time.sleep(config.ts_macd_trailing_delayt_time - time.time() % config.ts_macd_trailing_delayt_time)

                client = kwargs['client']
                trading_symbol = kwargs['trading_symbol']

                future_orders = Orders()

                first_block = 3
                first_block_activation = 3.2
                second_block = 7
                second_block_activation = 7

                first_block_callback = 2.8
                second_block_callback = 5

                position_amount, entry_price, unrealized_profit = self.future_action.future_position_data(client,
                                                                                                          trading_symbol,
                                                                                                          config.ts_macd_round)

                if second_block > unrealized_profit > first_block:
                    if position_amount > 0:
                        current_price = float(self.price_service.get_current_price(config.ts_macd_symbol))
                        activation = (entry_price * first_block_activation / 100) + entry_price
                        # activation_price = "{:.4f}".format(activation)
                        activation_price = round(float(activation), config.ts_macd_round)
                        if current_price < activation_price:
                            future_orders.cancel_all_open_orders(client, trading_symbol)
                            trailing = self.order.long_trailing_stop(client, config.ts_macd_symbol,
                                                                     config.ts_macd_pos_amount,
                                                                     activation_price, first_block_callback)
                            print(f"Trailing  activated {first_block} callbaback {first_block_callback}")


                    elif position_amount < 0:
                        current_price = float(self.price_service.get_current_price(config.ts_macd_symbol))
                        activation = entry_price - (entry_price * first_block_activation / 100)
                        activation_price = round(float(activation), config.ts_macd_round)
                        if current_price > activation_price:
                            future_orders.cancel_all_open_orders(client, trading_symbol)
                            trailing = self.order.short_trailing_stop(client, config.ts_macd_symbol,
                                                                      config.ts_macd_pos_amount,
                                                                      activation_price, first_block_callback)
                            print(f"Trailing  activated {first_block_activation} callbaback {first_block_callback}")

                if unrealized_profit > second_block:
                    if position_amount > 0:
                        current_price = float(self.price_service.get_current_price(config.ts_macd_symbol))
                        activation = (entry_price * second_block_activation / 100) + entry_price
                        # activation_price = "{:.4f}".format(activation)
                        activation_price = round(float(activation), config.ts_macd_round)
                        if current_price < activation_price:
                            future_orders.cancel_all_open_orders(client, trading_symbol)
                            trailing = self.order.long_trailing_stop(client, config.ts_macd_symbol,
                                                                     config.ts_macd_pos_amount,
                                                                     activation_price, second_block_callback)
                            print(f"Trailing  activated {second_block_activation} callbaback {second_block_callback}")



                    elif position_amount < 0:
                        current_price = float(self.price_service.get_current_price(config.ts_macd_symbol))
                        activation = current_price - (current_price * second_block_activation / 100)
                        activation_price = round(float(activation), config.ts_macd_round)
                        if current_price > activation_price:
                            future_orders.cancel_all_open_orders(client, trading_symbol)
                            trailing = self.order.short_trailing_stop(client, config.ts_macd_symbol,
                                                                      config.ts_macd_pos_amount,
                                                                      activation_price, second_block_callback)

                            print(f"Trailing  activated {second_block_activation} callbaback {second_block_callback}")
            except Exception as e:
                print(e)

    def control_position_profit(self, client, symbol, round_price, round_amount):

        timing = 0
        while True:

            try:
                time.sleep(config.ts_macd_profit_delay_time - time.time() % config.ts_macd_profit_delay_time)

                first_block_percent = 0.01
                second_block_percent = 3.0
                last_block_percent = 6.0

                position_amount, entry_price, unrealized_profit = self.future_action.future_position_data(client,
                                                                                                          symbol,
                                                                                                          round_price)
                current_price = float(self.price_service.get_current_price(symbol))
                unrealized_profit_percent = ((current_price - entry_price) / entry_price) * 100

                if timing == 0:  # close 50% of amount position
                    # if unrealized_profit_percent > first_block_percent and timing == 0:  # close 50% of amount position
                    # close position

                    first_block_activation = 3.2
                    first_block_callback = 2.8

                    amount_for_close_first = round(position_amount / 2.0, round_amount)
                    # amount_for_close_first = position_amount/2.0

                    # self.order.close_open_position_profit(client, symbol, amount_for_close_first)
                    self.order.cancel_all_open_orders(client, symbol)

                    if position_amount > 0:
                        activation = (entry_price * first_block_activation / 100) + entry_price
                        activation_price = round(activation, round_price)
                        new_position_amount, entry_price, unrealized_profit = self.future_action.future_position_data(
                            client,
                            symbol,
                            round_price)
                        trailing = self.order.long_trailing_stop(client, symbol, abs(new_position_amount),
                                                                 activation_price, first_block_callback)
                    if position_amount < 0:
                        activation = entry_price - (entry_price * first_block_activation / 100)
                        activation_price = round(activation, round_price)
                        new_position_amount, entry_price, unrealized_profit = self.future_action.future_position_data(
                            client, symbol, round_price)
                        trailing = self.order.short_trailing_stop(client, symbol, abs(new_position_amount),
                                                                  activation_price, first_block_callback)

                    timing += 1
                ### second block

                second_block_activation = 7
                second_block_callback = 5

                if unrealized_profit_percent > second_block_percent and timing == 1:  # close 50% of amount position
                    amount_for_close_first = round(position_amount / 2.0, round_amount)
                    # amount_for_close_first = position_amount/2.0

                    self.order.close_open_position_profit(client, symbol, amount_for_close_first)
                    self.order.cancel_all_open_orders(client, symbol)

                    if position_amount > 0:
                        activation = (entry_price * second_block_activation / 100) + entry_price
                        activation_price = round(activation, round_price)
                        new_position_amount, entry_price, unrealized_profit = self.future_action.future_position_data(
                            client,
                            symbol,
                            round_price)
                        trailing = self.order.long_trailing_stop(client, symbol, abs(new_position_amount),
                                                                 activation_price, second_block_callback)
                    if position_amount < 0:
                        activation = entry_price - (entry_price * second_block_activation / 100)
                        activation_price = round(activation, round_price)
                        new_position_amount, entry_price, unrealized_profit = self.future_action.future_position_data(
                            client, symbol, round_price)
                        trailing = self.order.short_trailing_stop(client, symbol, abs(new_position_amount),
                                                                  activation_price, second_block_callback)

                    timing += 1
                #### third block
                if unrealized_profit_percent > last_block_percent and timing == 2:  # close all  amount of position
                    amount_for_close_first = position_amount
                    self.order.close_open_position_profit(client, symbol, amount_for_close_first)
                    self.order.cancel_all_open_orders(client, symbol)
            except Exception as e:
                print(e)
