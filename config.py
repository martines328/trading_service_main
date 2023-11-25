import time

api_key_real = "4zNlXjOY0R7P0risFtbrofDvzzPjXTZutdPa8PXoUZx7ypJVajAtfu9ollaPwkNI"
api_secret_real = "k8p3ZmaFLOCTITWi2KeBb3tyMSbhtLmRtZC1lQjxWPwI4QA7fxAUPwKGsfnjz4Jt"


BINANCE_API_KEY_testnet = "c918f6403af5360d974839e4d86c104014c12161753e1a5b5cf81e8fe42cef2d"
BINANCE_SECRET_KEY_testnet = "eff3ac725ff3f6b7007d42330b379be67abfd3129d14ab932c3f19cc99a7ee7a"


apikey_spot = '325u4zxwLBUBrShKFCBC8TJ37QBmSz6BogvuWROv6nE8iLIVCzSvjasJeiqFBUxN'
apisecret_spot = '6D01DR6MCI21ZeihNJZR3wgDYMkucHHgO4KRzEg2qtDKGcvaAQPb0IfDKngqI90m'

timestamp = int(time.time() * 1000)
recvWindow = 5000

#trend Strategy
ts_symbol = "BNBUSDT"
ts_trend_interval = '15m'
ts_trend_start_time = '10 day ago UTC'
ts_pos_amount = 0.1
ts_delay_time = 10  #900
ts_trailing_activation_percent = 0.9
ts_callback_rate = 0.7

ts_manage_pos_interval = '1h'
ts_manage_start_time = '10 day ago UTC'
ts_manage_delayt_time = 300 #in sec for 1hours manage




#!!!!!!!!!!!!!!!!cci!!!!!!!!!!!!!!!!!!!!!!!!!!

#trading interval
interval = '3m'
start_time = '1 day ago UTC'
delayt_time = 180 #in sec

#trend interval
trend_interval = '1h'
trend_start_time = '2 day ago UTC'

position_quantity = 0.001
trading_symbol = 'BTCUSDT'
leverage = 7

trailing_activation_percent = 0.6
callback_rate = 0.5
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
ts_macd_pos_amount = 101
ts_macd_leverage = 7
ts_macd_delay_time = 10  #7200 3600
ts_macd_position_delay_time = 10  #60
ts_macd_trailing_activation_percent = 2
ts_macd_callback_rate = 1.9

ts_macd_round = 4


ts_macd_manage_pos_interval = '2h'
ts_macd_manage_start_time = '10 day ago UTC'
ts_macd_manage_delayt_time = 7200 #in sec for 1hours manage