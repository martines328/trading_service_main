import time

api_key_real = "m3S7fP39dVm799Bm82JoZezWyK6pJcnTW0jT29KFzBwHTBlPtqnyTzxp4ruRcx1P"
api_secret_real = "bwZavuplh3C3XqU1pi4UrOZtsSC6jQiyYpKNye8tHZj1H6dsuQtLAnjKHrlapg8P"


BINANCE_API_KEY_testnet = "8011427a15a11794bd3949e0e509cf2b3be22337a998304b8a449a5ea69fa20b"
BINANCE_SECRET_KEY_testnet = "817284769c94f0ebca99845ab60a742b979b10a98c8614bbf94348c761a464f7"


apikey_spot = '325u4zxwLBUBrShKFCBC8TJ37QBmSz6BogvuWROv6nE8iLIVCzSvjasJeiqFBUxN'
apisecret_spot = '6D01DR6MCI21ZeihNJZR3wgDYMkucHHgO4KRzEg2qtDKGcvaAQPb0IfDKngqI90m'

timestamp = int(time.time() * 1000)
recvWindow = 5000

# #trend Strategy
# ts_symbol = "BNBUSDT"
# ts_trend_interval = '15m'
# ts_trend_start_time = '10 day ago UTC'
# ts_pos_amount = 0.1
# ts_delay_time = 10  #900
# ts_trailing_activation_percent = 0.9
# ts_callback_rate = 0.7
#
# ts_manage_pos_interval = '1h'
# ts_manage_start_time = '10 day ago UTC'
# ts_manage_delayt_time = 300 #in sec for 1hours manage




#!!!!!!!!!!!!!!!!cci!!!!!!!!!!!!!!!!!!!!!!!!!!

#trading interval
interval = '3m'
start_time = '1 day ago UTC'
delayt_time = 300 #1800 in sec

#trend interval
trend_interval = '30m'
trend_start_time = '5 day ago UTC'

position_quantity = 0.002
trading_symbol = 'BTCUSDT'
leverage = 7
round_num = 1
trailing_activation_percent = 1.0
callback_rate = 0.9
#
# file_name_to_save = "result.txt"
# log_file = "logging.txt"
# _possition_ratio = 1.5
# SL_percent = 1
# TP_percent = SL_percent* _possition_ratio

#
# #willr
# interval_willr = '2h'
# start_time_willr = '5 day ago UTC'
# delayt_time_willr = 600 #in sec
# symbol_willr = "ETHUSDT"

# !!!!!!!!!! 2H MACD SuperTrendStrategy!!!!!!!!!!
ts_macd_symbol = "MATICUSDT"
ts_macd_interval = '2h'
ts_macd_interval_start_time = '15 day ago UTC'
ts_macd_pos_amount = 25
ts_macd_leverage = 7
ts_macd_delay_time = 3600  #300
ts_macd_position_delay_time = 5  #60
ts_macd_trailing_activation_percent = 2.5
ts_macd_callback_rate = 2.4

ts_macd_round = 4


ts_macd_manage_pos_interval = '2h'
ts_macd_manage_start_time = '10 day ago UTC'
ts_macd_manage_delayt_time = 7200 #in sec for 1hours manage
ts_macd_trailing_delayt_time = 300 #in sec for 1hours manage
ts_macd_profit_delay_time = 2 #in sec for 1hours manage




### SuperTrend Rsi STrategy
