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
            )
            print(f"Market order placed to close position: {order}")
        else:
            print("No open position to close.")

