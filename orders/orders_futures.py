import time

import config


class Orders():

    def cancel_all_open_orders(self, client, symbol):
        order = client.futures_cancel_all_open_orders(
            recvWindow=config.recvWindow,
            timestamp=config.timestamp,
            symbol=symbol)
        return order

    def placeSellOrder(self, client, symbol, quantity):
        orderSell = client.futures_create_order(
            symbol=symbol,
            side='SELL',
            type='MARKET',
            recvWindow=config.recvWindow,
            timestamp=config.timestamp,
            quantity=quantity,
            reduceOnly=False)
        return orderSell

    def placeBuyOrder(self, client, symbol, quantity):
        orderBuy = client.futures_create_order(
            symbol=symbol,
            side='BUY',
            type='MARKET',
            recvWindow=config.recvWindow,
            timestamp=config.timestamp,
            quantity=quantity,
            reduceOnly=False
        )
        return orderBuy

    def close_long(self, client, symbol, longTP):
        order = client.futures_create_order(
            symbol=symbol,
            side='SELL',
            type='TAKE_PROFIT_MARKET',
            stopPrice=longTP,
            closePosition='true',
            recvWindow=config.recvWindow,
            timestamp=config.timestamp
        )

    def close_short(self, client, symbol, shortTP):
        order = client.futures_create_order(
            symbol=symbol,
            side='BUY',
            type='TAKE_PROFIT_MARKET',
            stopPrice=shortTP,
            closePosition='true',
            recvWindow=config.recvWindow,
            timestamp=config.timestamp
        )

    #
    def long_trailing_stop(self, client, symbol, quantity, activation_price, callback_rate):
        order = client.futures_create_order(
            symbol=symbol,
            side='SELL',
            type='TRAILING_STOP_MARKET',
            reduceOnly=True,
            quantity=quantity,
            activationPrice=activation_price,
            callbackRate=callback_rate,
            recvWindow=config.recvWindow,
            timestamp=config.timestamp
        )
        return order

    def short_trailing_stop(self, client, symbol, quantity, activation_price, callback_rate):
        order = client.futures_create_order(
            symbol=symbol,
            side='BUY',
            type='TRAILING_STOP_MARKET',
            reduceOnly=True,
            quantity=quantity,
            activationPrice=activation_price,
            callbackRate=callback_rate,
            recvWindow=config.recvWindow,
            timestamp=config.timestamp
        )
        return order

    def close_open_position_market(self, client, symbol, quantity ):
        position = client.futures_position_information(symbol=symbol)
        current_position = float(position[0]['positionAmt'])
        # Close the position with a market order
        if current_position != 0:
            order = client.futures_create_order(
                symbol=symbol,
                side='SELL' if current_position > 0 else 'BUY',
                type='MARKET',
                quantity=abs(current_position),
                recvWindow=config.recvWindow,
                timestamp=config.timestamp
            )
            print(f"Market order placed to close position: {order}")
        else:
            print("No open position to close.")

    def close_open_position_profit(self, client, symbol, quantity ):
        position = client.futures_position_information(symbol=symbol)
        current_position = float(position[0]['positionAmt'])
        # Close the position with a market order
        if current_position != 0:
            order = client.futures_create_order(
                symbol=symbol,
                side='SELL' if quantity > 0 else 'BUY',
                type='MARKET',
                quantity=abs(quantity),
                recvWindow=config.recvWindow,
                timestamp=config.timestamp
            )
            print(f"Market order placed to close position: {order}")
        else:
            print("No open position to close.")

    def placeStopLossOrder(self, client, symbol, quantity, stop_loss_price, side):
        """
        Розміщує стоп-лос ордер для закриття позиції при досягненні стоп-лос ціни.

        :param client: Об'єкт клієнта Binance
        :param symbol: Символ торгової пари (наприклад, 'BTCUSDT')
        :param quantity: Кількість активів
        :param stop_loss_price: Ціна для стоп-лос ордера
        :param side: 'SELL' для лонгів або 'BUY' для шортів
        """
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type='STOP_MARKET',
            stopPrice=stop_loss_price,
            quantity=quantity,
            reduceOnly=True,
            recvWindow=config.recvWindow,
            timestamp=config.timestamp
        )
        print(f"Stop-loss order placed: {order}")
        return order