import datetime
import sys
from unittest import result
import environment
from api import *
from algorithm import *
from concurrent.futures import ProcessPoolExecutor
import logging
import UI
import gc


gc.collect() 
CT = datetime.datetime.today().replace(microsecond=0)  # ローカルな現在の日付と時刻を取得
logging.basicConfig(filename=fr'{CT.year}年{CT.month}月{CT.day}日{CT.hour}時{CT.minute}分.log', level=logging.INFO, encoding='utf-8')
logging.info(f'$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$開始:{CT}$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')

##############################
# 環境変数チェック
##############################
#print(environment.COIN)
print(UI.Config['coin'])
# 暗号通貨の判定
if not (UI.Config['coin']== 'btc' or 
        UI.Config['coin']== 'etc' or 
        UI.Config['coin']== 'fct' or
        UI.Config['coin']== 'omg' or 
        UI.Config['coin']== 'lsk' or  
        UI.Config['coin']== 'mona'):
    print('Invalid coin')
#   sys.exit()

################################以下は取引設定#############################################

#買いと同時に損切りの指値注文するか
loss_cut_sell:bool = True

#上記損切りの逆指値注文をキャンセルし、売買するか
cancel_loss_cut_sell:bool = True

#n時間ごとにメモリをリセットする
n = 4

######################################################################################


# レート取得
res_json = get_rate('sell', 0.005, None)
# APIが有効であるか確認する
is_valid_key = res_json['success']

# APIキーの判定
if not is_valid_key:
    print('Invalid API key.')
    sys.exit()

# 最小注文数量（円）
min_amount = 50000
# BTCの場合は0.005以上からしか購入できない
if UI.Config['coin'] == 'btc':
    min_amount = float(res_json['price'])


# 購入金額の設定
if UI.Config['amount']  is None or UI.Config['amount'] == '':
    # 未指定の場合は満額設定↓
    TradeJPY = float(get_status()['jpy']) #return 0
else:
    TradeJPY = float(UI.Config['amount'])
    #TradeJPY = get_amount()
if TradeJPY < min_amount:
    print(str(min_amount) + '円以上ご指定ください。')
    sys.exit()

print( UI.Config['coin'] + ' を ' + str(TradeJPY) + '円で取引予定。')
logging.info(f'{UI.Config[2]}を{TradeJPY}円で取引予定。')

# 本番の場合
if UI.Config['シミュレーションモード'] == False:
    print('##############################')
    print('####                      ####')
    print('####        本場取引！      ####')
    print('####                      ####')
    print('##############################')
    logging.info('##############################')
    logging.info('####                      ####')
    logging.info('####        本場取引！      ####')
    logging.info('####                      ####')
    logging.info('##############################')

logging.info(fr'設定　:{UI.Config}')

df = pd.DataFrame(columns=["timestamp","open","high","low","close","volume"])
#Ref5min = pd.DataFrame()
#####################################################チャートについてのインデックス
index5min:int = 1
#index30min:int = 1         
#index60min:int = 1

#####################################################
stoppingTrade :bool = False
stoppingTimeCount:int = 1
#####################################################
profit_list = (0,0)
diff_list = (0,0,0)
#####################################################

##################ここから取引処理###############################################

Ref5min = fetch_historical_data("BTC/JPY", CT + datetime.timedelta(hours = -2), CT,  interval=5)  

i = 1
j = 1

# 以下無限ループ
while True:
    gc.collect() 
    
    #フラグの初期化
    flgs_buy_1min = (False, False, False)
    flgs_buy_5min = (False, False, False)
    flgs_buy_30min = (False, False, False)
    flgs_buy_1hour = (False, False, False)
    flgs_buy_4hour = (False, False, False)
   
    flgs_sell_1min = (False, False, False)
    flgs_sell_5min = (False, False, False)
    flgs_sell_30min = (False, False, False)
    flgs_sell_1hour = (False, False, False)
    flgs_sell_4hour = (False, False, False)

    
    buy_flg :bool = False
    sell_flg :bool = False
    
    buying :bool = False
    selling :bool = False
    
    
    # df(一分足)の取得
    print("df(一分足)の取得")
    candle_stick = get_candle_stick(int(UI.Config['SamplingTime']))
 
    df = pd.concat([df, candle_stick], axis=0,ignore_index=True)
    print(f"                                                                                                                                                                        ")
    print(f"----------------------------------------------------------------------------------------{j}分目--------------------------------------------------------------------------")
    #print("dfの詳細")
    #print(df)

    if stoppingTrade == True:
        stoppingTimeCount = stoppingTimeCount + 1
        print('取引停止中です。')
        
        #if stoppingTimeCount == 4*60 :
        #    stoppingTrade = False
        #    stoppingTimeCount = 1
        #    print('取引を再開します。')
        #    CT = datetime.datetime.today().replace(microsecond=0)
        #    logging.info(fr'取引を再開します。{CT}')
    ##################################################################チャートについて
    

    Result5min = collecting_chart(df, Ref5min, index5min, 5, True)
    if ((Result5min[0] == int(index5min+1))):
        index5min = int(Result5min[0])
        Ref5min = Result5min[1]
    
        ###################################################################
    ###################################################################
    
    if(len(df)> 10):########################
        print("df(1分足)による判断")#0330
        
        Ref1min = df[-60:]
        
        Ref1min = Ref1min.reset_index(drop=True)
        flgs_buy_1min = Algorithm_Trade(Ref1min,UI.Config)[0]
        flgs_sell_1min = Algorithm_Trade(Ref1min,UI.Config)[1]
        #print(Ref1min)
        
    
    if (len(Ref5min)> 23):  
        print("5分足による判断")
        
        flgs_buy_5min = Algorithm_Trade(Ref5min,UI.Config)[0]
        flgs_sell_5min = Algorithm_Trade(Ref5min,UI.Config)[1]
        #print(Ref5min)
        
   
     
    flgs_buy_tupple = flgs_buy_1min + flgs_buy_5min + flgs_buy_30min + flgs_buy_1hour + flgs_buy_4hour
    flgs_sell_tupple = flgs_sell_1min + flgs_sell_5min + flgs_sell_30min + flgs_sell_1hour + flgs_sell_4hour
    
    ##############################2024/3/9###############################
    # 現在の時刻を取得
    current_time = datetime.datetime.today().replace(microsecond=0) 

    # 現在の時刻が22:00から25:00の間にあるかどうかを判定
    if (21 <= current_time.hour < 22) and (45 <= current_time.minute < 55) and (0 <= current_time.weekday() <= 4):
        
        print(f"現在は平日22:00から24:00の間です。取引を行います。")
        
        stoppingTrade = False
        buy_flg = True
        sell_flg = False
    
    elif (0 <= current_time.hour < 1) and (5 <= current_time.minute < 10) and (0 <= current_time.weekday() <= 4):
    
        print(f"24時を過ぎたので手仕舞いにします。")
        
        stoppingTrade = False        
        sell_flg = True
        buy_flg = False
        #stoppingTrade = True
          
    else: 
        print(f"現在は設定時間の間ではありません。参考までにフラグを出力しています。")
        
        stoppingTrade = True
        
        result = Trade_decider(UI.Config, flgs_buy_tupple, flgs_sell_tupple) 
        buy_flg:bool = result[0]
        sell_flg:bool = result[1]
        
        
    ##############################2024/3/9###############################
    
    coin_amount = get_status()[UI.Config['coin']] ##########コインチェックで制限されるとエラー起こる
    
    now_amount = df.iloc[-1]['close'] * coin_amount
    print(f'{coin_amount}BTC   ¥{now_amount}YEN分を保有')
    
    print(f'environment.order_id {environment.order_id }, environment.BUY_COIN_AMOUNT {environment.BUY_COIN_AMOUNT}, buy_flg {buy_flg}, sell_flg {sell_flg}, stoppingTrade {stoppingTrade} ')
          
      
        # 買い注文実施判定
    if ((environment.order_id is None) and  (environment.BUY_COIN_AMOUNT is None) and (buy_flg==True)):   #重要0
            buying :bool = True
            
            if any(flgs_buy_tupple):
                CTlog = datetime.datetime.today().replace(microsecond=0) 
                logging.info(f'StartBuy注文    {CTlog} ')
                logging.info(f'flgs_buy_tupple : {flgs_buy_tupple}')
            
            #ロスカット売りをキャンセルして購入する。本番のみ
            if((cancel_loss_cut_sell == True) and (environment.order_id_cancel is not None)):
                Cancel_LoscutSell(environment.PAIR, environment.order_id_cancel)
            
            
        # 売り注文実施判定
    if ((environment.order_id is not None) and  (environment.BUY_COIN_AMOUNT is not None) and (sell_flg==True)):  #重要①
            selling :bool = True
            
            if any(flgs_sell_tupple):
                CTlog = datetime.datetime.today().replace(microsecond=0) 
                logging.info(f'FinishSell注文    {CTlog} ')
                logging.info(f'flgs_sell_tupple : {flgs_sell_tupple}')
            
            #ロスカット売りをキャンセルして売却する。本番のみ
            if((cancel_loss_cut_sell == True) and (environment.order_id_cancel is not None)):
                Cancel_LoscutSell(environment.PAIR, environment.order_id_cancel)
    
    
    #####################################################################################
    
    if (buying == True and stoppingTrade == False):
        print(f'                                        {i}回目の取引')
        logging.info(fr'---------------------------------------------------------------------------{i}回目の取引----------------------------------------------------------------------------------------------------')
        CT = datetime.datetime.today().replace(microsecond=0)
        environment.buy_price = df.iloc[-1]['close']                        #######################フラグ処理に使おう
        logging.info(f'購入注文。購入金額:{int(TradeJPY)} Price:{environment.buy_price}                                                                      {CT}                                           ¥¥¥')
        #order_json = simulation_buy(get_amount()) if UI.Config['シミュレーションモード'] else buy(get_amount())
        order_json = simulation_buy(TradeJPY) if UI.Config['シミュレーションモード'] else buy(TradeJPY)

        # 買い注文成功の場合
        if order_json is not None:
            # オーダーIDをセット
            environment.order_id = order_json['id']
            # 購入金額をセット
            environment.market_buy_amount = float(order_json['market_buy_amount'])  
            # 購入COIN_AMOUNTをセット
            #environment.BUY_COIN_AMOUNT = float(order_json['amount'])
            environment.BUY_COIN_AMOUNT = float(environment.market_buy_amount/environment.buy_price)
            
            print(f'↑注文番号：{environment.order_id} 購入金額：{int(environment.market_buy_amount)}  COIN_AMOUNT: {environment.BUY_COIN_AMOUNT }')
            logging.info(f'↑注文番号：{environment.order_id} 購入金額：{int(environment.market_buy_amount)}  COIN_AMOUNT: {environment.BUY_COIN_AMOUNT}    Price:  {environment.buy_price}')
            
            ## ロスカットを設定　本番のみ　main.py    ln296
            if loss_cut_sell == True:
                LosscutSell(environment.buy_price, 0.977)
                
            
            # シミュレーションの場合
            if UI.Config['シミュレーションモード'] == True:
                environment.simulation_jpy -= TradeJPY
                environment.simulation_coin += float(order_json['amount'])
                
                
        elif order_json is None:
            buying = False
            print(f'購入できませんでした')
            logging.info(f'購入できませんでした')
                
    elif (selling==True) :#and stoppingTrade == False):2024.3.4
        # 売り注文実施
        print('Actual_Sell')
        CT = datetime.datetime.today().replace(microsecond=0)
        environment.sell_price = df.iloc[-1]['close']     ########################フラグ処理に使おう
        logging.info(fr'売却注文。注文番号:{environment.order_id}   Price:{environment.sell_price}                                                               {CT}                                          ¥¥¥¥¥¥¥¥¥¥¥¥¥')
        
        
        ##########保有BTCをすべて売却
        #order_json = simulation_sell(environment.simulation_coin) if UI.Config['シミュレーションモード']==True else sell(environment.order_id) 
        
        #要検討####買った分のBTCを売却。しかし、買った分のBTC（environment.BUY_COIN_AMOUNT）に微妙な誤差あり。
        order_json = simulation_sell(environment.simulation_coin) if UI.Config['シミュレーションモード']==True else mysell(environment.BUY_COIN_AMOUNT)
      
        
        # 売り注文成功の場合
        if order_json is not None:
            # オーダーIDを初期化
            environment.order_id = None
            environment.BUY_COIN_AMOUNT = None

            
            
            #environment.market_sell_amount = float(status['jpy'])  ###日本金の全額になる。利益の計算が少しバグる。指定金額はなるべく全額に近い値にするとよい
            
            # 利益を計算するためにレートを取得
            order_rate_json = get_rate('sell', order_json['amount'], None)
            
            environment.market_sell_amount = float(order_rate_json['price'])
            # 今回の取引の利益
            profit = environment.market_sell_amount - environment.market_buy_amount  ##########変更の余地あり
            profit = int(profit)
            environment.profit += profit
            
            status = get_status()
            logging.info(f'                                                                                    Price:{environment.sell_price}  直近の利益：{profit} ')
            print(f'----------------------------------ステータス:{status} {i}回目の取引を終えました--------------------------------------------------------------')
            logging.info(f'-------------------------ステータス:{status} {i}回目の取引を終えました-----------------------------------------------------------')
            
            i = i + 1
            
            # シミュレーションの場合
            if UI.Config['シミュレーションモード'] == True:
                environment.simulation_jpy += float(order_rate_json['price'])
                environment.simulation_coin = 0

            #########################################   以下はアセスメント  ######################################################################################
            
            profit = (profit,)
            profit_list = profit_list + profit
            print(profit_list)

            # 差分のリストを作成する
            diff1 = profit_list[-1] - profit_list[-2]
            diff1 = (int(diff1),)
            diff_list = diff_list + diff1

            #  listのlength調整
            if len(profit_list) > 7:
                profit_list = list(profit_list)
                profit_list.pop(0)
                profit_list = tuple(profit_list)
                
            if len(diff_list) > 8:
                diff_list = list(diff_list)
                diff_list.pop(0)
                diff_list = tuple(diff_list)

            #Assesment(environment.market_buy_amount:float, losscut_percent;float, profit_list:list, diff_list:list, profit):
            Assesment(environment.market_buy_amount, 0.03, profit_list, diff_list)
            
            environment.market_buy_amount = None
            environment.buy_price = 0 
            
            if TradeJPY < environment.market_sell_amount:
                print(f"投資成功！！！！！   {environment.market_sell_amount - TradeJPY}円")
                logging.info(f"投資成功！！！！！   {environment.market_sell_amount - TradeJPY}円")
                
            else:
                print(f"損失   {TradeJPY - environment.market_sell_amount}円") 
                logging.info(f"損失   {environment.market_sell_amount - TradeJPY}円")
                TradeJPY = environment.market_sell_amount * 0.999
            
            
             
        elif order_json is  None:
            selling = False
            print(f'売却できませんでした')
    
    
    
#################################   以下はメモリ対策 ######################################################################################    
    
    #n時間ごとにメモリをリセットする
    if len(df)> 60*n:
        
        # メモリ対策のためdf初期化
        CT = datetime.datetime.today().replace(microsecond=0)  
        print(f'メモリ対策のため、{n}時間までのdfを破棄し,初期化します。')
        logging.info(f'メモリ対策のため、{n}時間までのdfを破棄し,初期化します。{CT}')

        # 全ての行を削除
        df = df.drop(df.index[:])  
        Ref1min = Ref1min.drop(Ref1min.index[:])  

  
        if(len(Ref5min)>32):#8hで＋９６
        #    #Ref5min = Ref5min.drop(Ref5min.index[0:48])
            Ref5min = Ref5min.drop(Ref5min.index[:-30])
            Ref5min = Ref5min.reset_index(drop=True)
            logging.info(f'5分足を破棄します。')
            print(Ref5min)
            
              
        index5min:int = 1
        #index30min:int = 1
        #index60min:int = 1

        profit_list = (0,0)
        diff_list = (0,0,0)
        
    
    j = j + 1
        
    
        
