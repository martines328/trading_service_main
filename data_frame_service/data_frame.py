import pandas as pd


class Data_frame():

    def __init__(self):
        pass



    def get_last_kline_price(self, df):
        df['close'] = df['close'].astype(float)
        close_price_last = df['close'].iloc[-1]  # Ціна закриття останньої свічки
        close_price_prev = df['close'].iloc[-2]  # Ціна закриття передостанньої свічки
        return close_price_prev

    def get_data_frame(self, client,  symbol, interval, start_time):
        bars = client.get_historical_klines(symbol, interval=interval, start_str=start_time)

        for line in bars:  # Keep only first 5 columns, "date" "open" "high" "low" "close"
            del line[6:]

        df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close', 'volume'])  # 2 dimensional tabular data
        df['date'] = pd.to_numeric(df["date"], errors='coerce')
        df["open"] = pd.to_numeric(df["open"], errors='coerce')
        df["high"] = pd.to_numeric(df["high"], errors='coerce')
        df["low"] = pd.to_numeric(df["low"], errors='coerce')
        df["close"] = pd.to_numeric(df["close"], errors='coerce')
        df["volume"] = pd.to_numeric(df["volume"], errors='coerce')
        # df.to_csv('dff.csv', index=False)
        return df

