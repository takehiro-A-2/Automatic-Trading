import os
from coincheck.coincheck import CoinCheck
coinCheck = CoinCheck(os.environ.get('ACCESS_KEY'), os.environ.get('API_SECRET'))
import environment
import UI
import requests
import pandas as pd
import datetime
import zoneinfo
import logging
from datetime import timezone, timedelta
import json
import time
import pandas as pd
import csv
import gc
import platform

os_name = platform.system()

# 必要モジュールのインポート
from dotenv import load_dotenv
# .envファイルの内容を読み込見込む
load_dotenv()

from retry import retry

def fetch_historical_data(symbol, start_date, end_date, interval=60):
    
    # Unixタイムスタンプに変換
    start_timestamp = int(start_date.timestamp())
    #end_timestamp = int(end_date.timestamp())
 
    # KrakenのOHLCエンドポイントURL
    url = 'https://api.kraken.com/0/public/OHLC'
 
        # パラメータの設定
    params = {
            'pair': symbol,
            'interval': interval,
            'since': start_timestamp
        }
 
        # APIリクエストを実行
    response = requests.get(url, params=params)
 
        # レスポンスの確認
    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}")
 
        # データの抽出
    data = response.json()
    #print("data from Kraken")
    #print(data)
 
        # 結果を確認
    if data['error']:
        print('Cant Get From Kraken')
        df = pd.DataFrame(columns=["timestamp","open","high","low","close","volume"])
        return df

    new_data = pd.DataFrame(data['result'][symbol], columns=[
            "timestamp","open","high","low","close", 
            'VWAP',
             'volume',
             'Count',
             ])
             
    #print('AllFromKraken')
    #print(new_data)
    
    #ika Kraken kara no data.wo kakou
    #print('DeletePart')
    
    # JSTのタイムゾーンオブジェクトを作成
    jst_timezone = timezone(timedelta(hours=9))  # 日本時間はUTC+9

    # Timestamp列をJSTに変換
    new_data['timestamp'] = pd.to_datetime(new_data['timestamp'], unit='s').dt.tz_localize('UTC').dt.tz_convert(jst_timezone)
    
    #Delete no_use signal
    new_data = new_data.drop('VWAP', axis=1)
    new_data = new_data.drop('Count', axis=1)
    
    #Modify signal var
    new_data['open'] = new_data['open'].astype(int)
    new_data['high'] = new_data['high'].astype(int)
    new_data['low'] = new_data['low'].astype(int)
    new_data['close'] = new_data['close'].astype(int)
    new_data['volume'] = new_data['volume'].astype(float)
    
    #print(new_data)
    
  ##Definite df 
    df = pd.DataFrame(columns=["timestamp","open","high","low","close","volume"])
    
    df = new_data
    print('df')
    print(df)
    gc.collect() 

    return df


def get_candle_stick(SamplingTime:int = 1):
    """
    1分間のローソク足を算出する

    :rtype: object
    """
    #candle = {}
    candle = pd.DataFrame(columns=["timestamp","open","high","low","close","volume"])
    
    for sec in range(1, int(int(environment.INTERVAL)/SamplingTime) + 1):
        data = get_latest_trading_rate()
        price = int(data)
     
        
        if sec == 1:
            #candle.at[0,"timestamp"] = data['created_at']
            candle.at[0,"open"] = price
            candle.at[0,"high"] = price
            candle.at[0,"low"] = price
            #candle['close'] = price
        elif (sec == int(int(environment.INTERVAL)/SamplingTime)):
            #candle['close'] = price
            candle.at[0,"close"] = price
            
            #
            CTcandle= datetime.datetime.today().replace(microsecond=0)  
            candle.at[0, "timestamp"] = CTcandle
            

        if sec != 1:
            candle.at[0,"high"] = price if price > candle.at[0,"high"] else candle.at[0,"high"]
            candle.at[0,"low"] = price if price < candle.at[0,"low"] else candle.at[0,"low"]

        var = {
            'profit': environment.profit,
            'market_buy_amount': str(environment.market_buy_amount),
            'order_id': environment.order_id,
            'COIN': environment.COIN,
        }
        print(str(sec*SamplingTime).zfill(2) + '秒 ステータス: ' + str(var) + ' ローソク足: ' + f'open:  {str(candle.at[0,"open"])}, high:  {candle.at[0,"high"]}, low:  {candle.at[0,"low"]}, close:  {candle.at[0,"close"]}')
        time.sleep(int(SamplingTime))###
        
        #candle = candle.astype('int')
        
    return candle

@retry(exceptions=Exception, delay=1)
def get_latest_trading_rate():
    """
    最新の取引レートを取得する

    :rtype: float
    """
    if environment.COIN == 'btc':
        ticker = coinCheck.ticker.all()
        return json.loads(ticker)['last']

    params = {
        'pair': environment.PAIR
    }
    trade_all = coinCheck.trade.all(params)
    #print(trade_all)
    data = json.loads(trade_all)['data']
    print('dataについて')
    print(data)
    return float(data[0]['rate'])

@retry(exceptions=Exception, delay=1)
def get_rate(order_type, coin_amount, price):
    """
    レートを取得する

    :rtype: object
    """
    if coin_amount is not None:
        params = {
            'order_type': order_type,
            'pair': environment.PAIR,
            'amount': coin_amount
        }
    else:
        params = {
            'order_type': order_type,
            'pair': environment.PAIR,
            'price': price
        }
    order_rate = coinCheck.order.rate(params)
    return json.loads(order_rate)


 

def buy(market_buy_amount):
    """
    指定した金額で買い注文を入れる（成行）
    :rtype: object
    """

    params = {
        'pair': environment.PAIR,
        'order_type': 'market_buy',
        'market_buy_amount': market_buy_amount,  # 量ではなく金額
    }

    order = coinCheck.order.create(params)
    order_create_json = json.loads(order)
    print(order_create_json)
    logging.info(f"order_create_json {order_create_json}")
    
    if order_create_json['success']:
        return order_create_json

    else:
        print(order)
        return None
 

def mysell(COIN_AMOUNT:float):
    params = {
        'pair': environment.PAIR,
        'order_type': 'market_sell',
        'amount': COIN_AMOUNT ,
        }
    
    order = coinCheck.order.create(params)
    order_create_json = json.loads(order)
    print(order_create_json)
    logging.info(f"order_create_json {order_create_json}")
    
    if order_create_json['success']:
        return order_create_json
    else:
        print(order)
    return None

 

def simulation_buy(market_buy_amount):
    """
    シミュレーション：指定した金額で買い注文を入れる（成行）
    :rtype: object
    """
    order_rate = get_rate('buy', None, market_buy_amount)
    return {
        'id': 'simulation',
        'market_buy_amount': market_buy_amount,
        'amount': order_rate['amount']}
    

def simulation_sell(COIN_AMOUNT:float):

    """
    シミュレーション：購入した量で売り注文を入れる（成行）
    :rtype: object
    """
    return {'amount': COIN_AMOUNT}

 

 


def get_status():
    """
    現在の状態を取得する

    :rtype: object
    """
    if environment.simulation:
        return {
            'profit': environment.profit,  # 利益
            'jpy': environment.simulation_jpy,  # 円
            environment.COIN: environment.simulation_coin,  # COIN
        }

    account_balance = coinCheck.account.balance()
    account_balance_json = json.loads(account_balance)
    if account_balance_json['success']:
        return {
            'profit': environment.profit,  # 利益
            'jpy': account_balance_json['jpy'],  # 円
            environment.COIN: float(account_balance_json[environment.COIN]),  # COIN
        }
    else:
        return account_balance_json


def collecting_chart(df:pd.DataFrame, Refmin:pd.DataFrame, count:int, min:int, no_record:bool): 
    df.fillna(0, inplace=True)
    # min分足のローソク足
    if ((((len(df))%int(min)) == 0 )and(len(df != 0))):#########
        
        if count  == 1 and len(Refmin) == 0:
            print('1回目！！'+str(count))
            
            #init1 = df.iat[0, 0]
            #init1 = df.iat[0,"open"] 
            Refmin = pd.DataFrame(columns=["timestamp","open","high","low","close","volume"])
            
            Refmin.at[0,"open"] = int(df.at[0,"open"])
            Refmin.at[0,"high"] = int(df['high'].max())
            Refmin.at[0,"low"] = int(df['low'].min())
            Refmin.at[0,"close"] = int(df.iat[-1, 4])
            
            CTcandle= datetime.datetime.today().replace(microsecond=0)  
            Refmin.at[0, "timestamp"] = CTcandle
            
            Refmin.fillna(0, inplace=True)

        if count != 1 or len(Refmin) > 0:  #####R1が入れないor
            print(f'{min}分足の更新→ {str(count)}回目')
            
            Candlemin = pd.DataFrame(columns=["timestamp","open","high","low","close","volume"])###323
            
            indexn = int(min*(count-1)) ####################
            #initn = df.iat[indexn, 'open']
            maxn = df['high'].iloc[indexn:].max()
            minn = df['low'].iloc[indexn:].min()
            
            Candlemin.at[0,"open"] = int(df.iat[indexn, 1])
            Candlemin.at[0,"high"] = int(maxn)
            Candlemin.at[0,"low"] = int(minn)
            Candlemin.at[0,"close"] = int(df.iat[-1, 4])
            
            CTcandle= datetime.datetime.today().replace(microsecond=0)  
            Candlemin.at[0, "timestamp"] = CTcandle
            
            Candlemin.fillna(0, inplace=True)
            
            #print(Candlemin)
           
            Refmin = pd.concat([Refmin, Candlemin],axis=0, ignore_index=True)###323
        
        
        # OSに応じた処理を行う
        if os_name == "Windows" and no_record == False:
            print("Hello World for Windows!")
            with open(fr'C:\Users\たけ\Desktop\チャート\{min}分足.csv', 'a', newline="") as f:  
                writer = csv.writer(f)
                CT = datetime.datetime.now().replace(microsecond=0)
                writer.writerow([fr'{CT.year}/{CT.month}/{CT.day}', f'{CT.hour}:{CT.minute}:{CT.second}', Refmin['open'].iloc[-1], Refmin['high'].iloc[-1], Refmin['low'].iloc[-1], Refmin['close'] .iloc[-1]])
                
        elif os_name == "Darwin" and no_record == False:
            print("Hello World for MacOS!")
            with open(f'/Users/mac/Desktop/チャート/{min}分足.csv', 'a', newline="") as f:   
                writer = csv.writer(f)
                CT = datetime.datetime.now().replace(microsecond=0)
                writer.writerow([f'{CT.year}/{CT.month}/{CT.day}', f'{CT.hour}:{CT.minute}:{CT.second}', Refmin['open'].iloc[-1], Refmin['high'].iloc[-1], Refmin['low'].iloc[-1], Refmin['close'] .iloc[-1]])
                
        else:
            #print("Unknown OS! Hello World anyway!")
            print("チャートは記録していません。")
    
        
        count = count +1 
        gc.collect() 
        return (count, Refmin,)
    
    return (count,)

#############################################


def Cancel_LoscutSell(PAIR, order_id_cancel):
    params_cancel = {
        'pair': PAIR,
        'id': order_id_cancel
        }
    order_cancel = coinCheck.order.cancel(params_cancel)  ##キャンセル
    CT = datetime.datetime.today().replace(microsecond=0)

    print(f'逆指値注文をキャンセルしました。')
    logging.info(f'逆指値注文をキャンセルしました。ID:{environment.order_id_cancel} 時刻：{CT}')

    environment.order_id_cancel = None
    #environment.market_buy_amount = None

 

def LosscutSell(buy_price, Losscut_ratio:float):
    
    loss_cut_rate :float = buy_price * Losscut_ratio#0.977 #-2.33％の値で逆指値注文
    
    print(f"ロスカットは{environment.BUY_COIN_AMOUNT}BTCを{loss_cut_rate}レートで損切りします。")
    logging.info(f"ロスカットは{environment.BUY_COIN_AMOUNT}BTCを{loss_cut_rate}レートで損切りします。")
    
    params = {
        'pair': environment.PAIR,
         #'order_type': 'sell',
        "order_type": "market_sell",  ###sellではなく、market_sell
         #"amount": coin_amount,
         #"amount": 0.005,
         "amount": environment.BUY_COIN_AMOUNT,      #environment.market_buy_amount,   ###要調査　COIN量か、金額か          
         #"rate": loss_cut_rate,
         #"rate": 4000000,
         "stop_loss_rate": loss_cut_rate  ##ここを指定して逆指値となる
    }
    order = coinCheck.order.create(params)
    order_json = json.loads(order)
    environment.order_id_cancel = order_json['id']

    CT = datetime.datetime.today().replace(microsecond=0)
    print(f'逆指値注文しました。')
    logging.info(f'逆指値注文しました。ID:{environment.order_id_cancel} 設定金額:{loss_cut_rate} 時刻：{CT}')

 

 
def Assesment(market_buy_amount:float, losscut_percent:float, profit_list:list, diff_list:list):
    
    # 3%以上の損失を出しているか
    loss = market_buy_amount * losscut_percent + profit_list[-1]
    bigloss_flg = loss < 0
    
    #3連続で得られた利益が負かどうか
    minusprofit_flg = (profit_list[-1] < 0 and profit_list[-2] < 0 and profit_list[-3] < 0)

    #4連続で得られる利益が減少している
    down_flg = (diff_list[-1] < 0 and diff_list[-2] < 0 and diff_list[-3] < 0 and diff_list[-4] < 0)  ##そもそもマイナス利益のばあいはばぐる

                
    print(f'loss_flg:{bigloss_flg} down_flg:{down_flg}')
    logging.info(f'loss_flg:{bigloss_flg} down_flg:{down_flg}')
 
     # 3%以上の損失を出している、または 3連続で利益がマイナス または 4連続で得られる利益が減少している 場合は一時停止する
    if (bigloss_flg==True or minusprofit_flg==True or down_flg==True):

        print(f'直近の利益。{profit_list}')
        print(f'3%以上の損失を出しているか。bigloss_flg:{bigloss_flg}')

        logging.info(f'3%以上の損失を出しているか。bigloss_flg:{bigloss_flg}')

        print(f'3連続で利益がマイナスか。minusprofit_flg:{minusprofit_flg}')

        logging.info(f'3連続で利益がマイナスか。minusprofit_flg:{minusprofit_flg}')
        print(f'4連続で得られる利益が減少しているか。down_flg:{down_flg}')

        logging.info(f'4連続で得られる利益が減少しているか。down_flg:{down_flg}')

        ##############2024.3.4####
       #if not UI.Config['シミュレーションモード']:

           #CT = datetime.datetime.today().replace(second=0, microsecond=0)
           #print(f'{CT} 4時間停止します。)')
           #logging.info(f'{CT} 4時間停止します。')
           #4時間buying == Falseとする
           #stoppingTrade = True
           
    return bigloss_flg, minusprofit_flg, down_flg,# stoppingTrade

 


#########################使わないメゾット##################################
#########################################################################

def data_collecting(how_many_samples=3, SamplingTime = 1):
    """
    初めの数回は取引をせずに価格データを集める

    :rtype: price_list
    """
    
    print('Collecting data... (' + str(how_many_samples*int(environment.INTERVAL)) + ' sec)')
    
    for i in range(1, how_many_samples + 1):
        candle = get_candle_stick(SamplingTime)
        df = pd.DataFrame(columns=["timestamp","open","high","low","close","volume"])###323
        df = pd.concat([df, candle],axis=0, ignore_index=True)###323
        
        #df = df.append({'open': candle['open'], 'high': candle['high'], 'low': candle['low'], 'close': candle['close'],}, ignore_index=True)
        print(str(i) + '/' + str(how_many_samples) + ' finish.')
    print('Collection is complete!')
    return df


def sell(order_id):
    """
    購入した量で売り注文を入れる（成行）

    :rtype: object
    """
    transactions = coinCheck.order.transactions()
    for transaction in json.loads(transactions)['transactions']:
        if order_id == transaction['order_id']:
            # TODO 買い注文が2つに分かれてるときがあるので一旦、全額売却にしておく
            # coin_amount = transaction['funds'][COIN]
            coin_amount = get_status()[environment.COIN]
            params = {
                'pair': environment.PAIR,
                'order_type': 'market_sell',
                'amount': coin_amount,
            }
            order = coinCheck.order.create(params)
            order_create_json = json.loads(order)
            print(order_create_json)
            logging.info(f"order_create_json {order_create_json}")

            if order_create_json['success']:
                return order_create_json
            else:
                print(order)
                return None

def get_amount():
    """
    購入金額を取得する

    :rtype: float
   
    """
    if UI.Config['amount']  is None or UI.Config['amount'] == '':
        # 未指定の場合は満額設定↓
        return float(get_status()['jpy'])
        #return 0
    else:
        return float(UI.Config['amount'])
        

def sleep(hour):
    """
    指定した時間停止する
    """
    interval:int = (int(environment.INTERVAL) * int(hour))
    for minute in range(0, int(interval)):
        print(f'現在時間：{int(minute)} 分 待機時間：{int(interval)} 分')
        for sec in range(1, (int(environment.INTERVAL) + 1)):
            #print(str(sec).zfill(2) + 'sec...')
            time.sleep(1)
