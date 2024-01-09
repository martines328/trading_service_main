import config
from client_service.client import Client


class Clietn_future_action():

    def change_position_margin_type(self,client,symbol, margin_type):
        response = client.futures_change_margin_type(symbol=symbol, marginType=margin_type)

    def change_position_margin(self,client,trading_symbol ,position_amount,new_callBack_rate):
        response = client.futures_change_position_margin(symbol=trading_symbol, amount=abs(position_amount), type=1,
                                                         timestamp=config.timestamp, callbackRate=new_callBack_rate)

    def check_open_position_bool(self, client, symbol: str) :
        pos = client.futures_position_information()
        for n in pos:
            if n['symbol'] == symbol:
                pos_amount = float(n['positionAmt'])
                if pos_amount and (pos_amount>0.0 or pos_amount<0.0):
                    return True,
                else: return False


    def future_position_data(self, client, symbol, price_round:int):
        pos = client.futures_position_information()
        for order in pos:
            if order['symbol'] == symbol:
                pos_amount = float(order['positionAmt'])
                entry_price = round(float(order['entryPrice']),price_round )
                unrealized_profit = float(order['unRealizedProfit'])
                # print(f"Open Order - Symbol: {order['symbol']}, Side: {order['side']}, Type: {order['type']}, Quantity: {order['origQty']}, Price: {order['price']}")
                return  pos_amount, entry_price, unrealized_profit


    def client_future_balance(self, client):
        b = client.futures_account_balance(recvWindow=config.recvWindow,
                timestamp=config.timestamp)
        for i in b:
            if i['asset'] == 'USDT':
                return print(f"Current client balance -- {float(i['balance'])} USDT")

    def change_leverage(self, client, trading_symbol, leverage):
        try:
            leverage = client.futures_change_leverage(
                symbol=trading_symbol,
                leverage=leverage,
                recvWindow=config.recvWindow,
                timestamp=config.timestamp
            )
            print(f"{leverage['symbol']} -- leverage - {leverage['leverage']}")
        except Exception as e:
            print(e)
