import pandas_ta as ta
import logging


class Indicators:

    def __init__(self, dframe):
        self.df = dframe

    def macd(self, shortMA=12, longMA=26, signal=9, macd_num=1, signal_num=1):
        # symbol_df = get_data_frame(client)

        # calculate short and long EMA mostly using close values
        shortEMA = self.df['close'].ewm(span=shortMA, adjust=False).mean()
        longEMA = self.df['close'].ewm(span=longMA, adjust=False).mean()

        # Calculate MACD and signal line
        MACD = shortEMA - longEMA
        signal = MACD.ewm(span=signal, adjust=False).mean()

        last_macd_data = MACD.values.tolist()
        last_signal_data = signal.values.tolist()

        macd = last_macd_data[-macd_num]
        signal = last_signal_data[-signal_num]

        if macd != None and signal!=None:
            logging.info("Calculated macd was successful")
        else:
            logging.warning("Macd wasn't calculated, check parametrs")

        return macd, signal


    def mfi(self, lenght:int, number:int):
        mfi = ta.mfi(self.df["high"], self.df["low"], self.df["close"],self.df["volume"], lenght)
        mfi_list = mfi.values.tolist()
        return mfi_list[-number]



    def ema(self, lenght: int):
        ema = ta.ema(self.df['close'], lenght)
        ema_list = ema.values.tolist()
        return ema_list[-1]

    def rsi(self, number: int):
        rsi_data = ta.rsi(self.df['close'], 14)
        rsi_list = rsi_data.values.tolist()
        return rsi_list[-number]

    def supertrend(self, number, length: int, multiplier: float, round_number=4):
        sptrnd = ta.supertrend(self.df["high"], self.df["low"], self.df["close"],
                               length=length, multiplier=multiplier)
        spr = sptrnd[f'SUPERT_{length}_{multiplier}'].values.tolist()
        # spr = sptrnd['SUPERT_10_1.5'].values.tolist()
        #supertr = "{:.4f}".format(spr[-number])
        supertr = round(spr[-number], round_number)

        if supertr != None :
            logging.info("Calculated supertrend was successful")
        else:
            logging.warning("Supertrend wasn't calculated, check parametrs")

        return supertr

    def stc(self, number, tclenght=16, fastLenght=29, slowLenght=38, round_number=1):
        stc_indicator = ta.stc(self.df["close"], tclenght, fastLenght, slowLenght)
        # stc_indicator = ta.stc(self.df["close"])
        print(stc_indicator)
        stc = stc_indicator[f'STC_{tclenght}_{fastLenght}_{slowLenght}_0.5'].values.tolist()
        stcf = round(stc[-number], round_number)

        # return 1
        return stcf



    def mcgnd(self,length=14):
        mcginley = ta.mcgd(self.df['close'], n=length)
        print("d")


    def williamsR(self, number):
        willr = ta.willr(self.df["high"], self.df["low"], self.df["close"], )
        will = willr.values.tolist()
        return will[-number]

    def cci_trend(self, number, round_number=2):
        ccind = ta.cci(self.df["high"], self.df["low"], self.df["close"], length=50)
        # print(ccind)
        cci = ccind.values.tolist()
        numb_cci = round(cci[-number], round_number)

        if numb_cci != None:
            logging.info("Calculated CCI was successful")
        else:
            logging.warning("CCI wasn't calculated, check parametrs")

        return numb_cci
