import numpy as np
import pandas as pd
import gc
#from concurrent.futures import ProcessPoolExecutor
#import sys
#import os
#import environment
#import UI



    # ボリンジャーバンドの判定
def bollinger_bands(df,duration, sigma):  
    
    duration = int(duration)
    # σの値
    sigma = int(sigma)

    # 移動平均
    df['SMA'] = df['close'].rolling(window=duration).mean()
    # 標準偏差
    df['std'] = df['close'].rolling(window=duration).std()

    # σ区間の境界線
    df['-' + str(sigma) + 'σ'] = df['SMA'] - sigma * df['std']
    df['+' + str(sigma) + 'σ'] = df['SMA'] + sigma * df['std']

    print('-' + str(sigma) + 'σ: ' + str(df.iloc[-1]['-' + str(sigma) + 'σ']))
    print('+' + str(sigma) + 'σ: ' + str(df.iloc[-1]['+' + str(sigma) + 'σ']))

    # 最新の値段が±xσを超えているか判定
    buy_flg = df.iloc[-1]['close'] < df.iloc[-1]['-' + str(sigma) + 'σ']     
    sell_flg = df.iloc[-1]['close'] > df.iloc[-1]['+' + str(sigma) + 'σ']
   
    return (buy_flg, sell_flg)

    # MACDの判定
def macd(df):

    macd = pd.DataFrame()
    macd['close'] = df['close']
    macd['ema_12'] = df['close'].ewm(span=12).mean()
    macd['ema_26'] = df['close'].ewm(span=26).mean()

    macd['macd'] = macd['ema_12'] - macd['ema_26']
    macd['signal'] = macd['macd'].ewm(span=9).mean()
    macd['histogram'] = macd['macd'] - macd['signal']

    print(str(macd.iloc[-2]['histogram']) + ' -> ' + str(macd.iloc[-1]['histogram']))

    # ヒストグラムが負から正になったとき（MACDがシグナルを下から上に抜けるとき）
    buy_flg = macd.iloc[-2]['histogram'] < 0 < macd.iloc[-1]['histogram']
    # ヒストグラムが正の状態で減少したとき
    sell_flg = macd.iloc[-2]['histogram'] > 0 and macd.iloc[-2]['histogram'] > macd.iloc[-1]['histogram']
    
    
    return (buy_flg, sell_flg)

    # RSIの判定
def rsi(df, duration, min, max):


    duration = int(duration)  
    

    df['diff'] = df['close'].diff()
    diff = df['diff'][1:]

    up, down = diff.copy(), diff.copy()
    up[up < 0] = 0
    down[down > 0] = 0

    up_sma_14 = up.rolling(window=duration, center=False).mean()
    down_sma_14 = down.abs().rolling(window=duration, center=False).mean()

    # RSIの計算
    df['rs'] = up_sma_14 / down_sma_14
    df['rsi'] = 100.0 - (100.0 / (1.0 + df['rs']))
    print('RSI: ' + str(df['rsi'].iloc[-1]))

    # RSIが設定値を下回ったとき
    buy_flg = float(df['rsi'].iloc[-1]) < float(min)
    # RSIが設定値を上回ったとき
    sell_flg = float(df['rsi'].iloc[-1]) > float(max)
    
    return (buy_flg, sell_flg)

    
def Algorithm_Trade(df,Config):
    
    gc.collect() 
    macd_ = macd(df)

    rsi_ = rsi(df, 18, Config['RSI_min'], Config['RSI_max'])

    boll_ = bollinger_bands(df, 10, Config['sigma'])
    
    flgs_buy = (macd_[0], rsi_[0], boll_[0])
    flgs_sell = (macd_[1], rsi_[1], boll_[1])
    
    
    return (flgs_buy, flgs_sell)


def Trade_decider(Config, flgs_buy_tupple, flgs_sell_tupple):#0330
    print("Trade_decider内部")
    
    buy_flg :bool = False
    sell_flg :bool = False
    
    Score_array = Config[15:-1].values.astype('float32')###.T
    print(f'コンフィグ:{Score_array}')
    
    flgs_buy_array = np.array(flgs_buy_tupple).astype('int')
    print(f'買いフラグ:{flgs_buy_array}')
    flgs_sell_array = np.array(flgs_sell_tupple).astype('int')
    print(f'売りフラグ:{flgs_sell_array}')
    

    buy_flg_count :float = 0
    #buy_flg_count = np.dot(flgs_buy_array, Score_array)
    buy_flg_count = np.sum(flgs_buy_array*Score_array)   ##アダマール積をとった後の要素の総和

    sell_flg_count :float = 0
    #sell_flg_count = np.dot(flgs_sell_array, Score_array)
    sell_flg_count = np.sum(flgs_sell_array*Score_array)
        
    print(f"買いの設定値:{Config['total_buyScore']}")
    print(f"売りの設定値:{Config['total_sellScore']}")
    print(f"買いの得点: {buy_flg_count}  >=  {Config['total_buyScore']}")
    print(f"売りの得点: {sell_flg_count}  >=  {Config['total_sellScore']}")
    
    buy_flg = buy_flg_count >= float(Config['total_buyScore'])
    sell_flg = sell_flg_count >= float(Config['total_sellScore']) ############  得点のアルゴリズム
    
    gc.collect() 
    return (buy_flg, sell_flg)



def create_result(buy_flg, sell_flg):
    
    return {
        'buy_flg': buy_flg,
        'sell_flg': sell_flg
    }
    

def difference(df):
    
    df['diff'] = df['close'].diff()

    # 下降→上昇
    buy_flg = df.iloc[-2]['diff'] < 0 < df.iloc[-1]['diff']
    # 上昇→下降
    sell_flg = df.iloc[-2]['diff'] > 0 > df.iloc[-1]['diff']

    print(str(df.iloc[-2]['diff']) + ' -> ' + str(df.iloc[-1]['diff']))

    
    return (buy_flg, sell_flg)
