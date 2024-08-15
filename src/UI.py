import datetime
# csvモジュールを使ってCSVファイルから1行ずつ読み込む
import csv
import platform
os_name = platform.system()
import PySimpleGUI as sg
import numpy as np
import pandas as pd
from main import *
import gc
 
 
def make_main():
    # ------------ メインウィンドウ作成 ------------
 
    Main_layout = [
        [sg.Text("新規"),sg.Text("初期設定"), ],
        [sg.Button('+',size=(1, 1), key='-ADD-'), sg.Button('初期設定', key='-APIConfig-')],
        [sg.Text("最近の設定")],
        [sg.Button('〇▽□', key='-ADD-')],  ##CSVから読みこむ。保存された名前と日時を記載したボタンを作成。保存数に応じてボタンが増える。（大変だ）
        ]
 
    Main_window = sg.Window("【ホーム画面】トレードアルゴリズムへようこそ!", Main_layout, size=(800, 600))
    return Main_window
 
#################################################
 
#3タブを関数化【Python】簡単！PySimpleGUIの画面遷移の方法３選！ (teru2teru.com)
def make_sub():
    
    # ------------ サブウィンドウ作成 ------------
 
# サイズが最大のものに統一される。この場合は(12, 7)が最大なのでタブ画面はすべて(12, 7)となる
    layout_1 = [[sg.Text("概要", size=(12, 1))]]
    layout_2 = [[sg.Text("アルゴリズム設定", size=(12, 3))]]
    layout_3 = [[sg.Text("得点・足設定", size=(12, 5))]]
    layout_4 = [[sg.Text("フローチャート設定", size=(20, 10))]]
 
    #coin = *pair取引ペア。現在は btc_jpy, etc_jpy, lsk_jpy, mona_jpy, omg_jpy, plt_jpy, fnct_jpy
    layout1 = [
        [sg.Text("設定名")],
        [sg.InputText(key='ConfigName')],
 
        #[sg.Text("シミュレーションモード")],
        [sg.Checkbox('シミュレーションモード  （チェックを外すと本番取引となります。）', key = 'シミュレーションモード', default=True),],
 
        [sg.Text("種類")],
        #[sg.Spin(itm,size=(10,5),initial_value=['bc/jy'],sg.Button('決定'))],
        [sg.Radio('BTC/JPY', key = 'BTC/JPY', group_id='a1',default=True),sg.Radio('ETC/JPY', key = 'ETC/JPY', group_id='a1',default=False),sg.Radio('LSK/JPY', key = 'LSK/JPY', group_id='a1',default=False),
         sg.Radio('MONA/JPY', key = 'MONA/JPY', group_id='a1',default=False),sg.Radio('OMG/JPY', key = 'OMG/JPY', group_id='a1',default=False),sg.Radio('PLT/JPY', key = 'PLT/JPY', group_id='a1',default=False),], #sg.Button('決定', key='-Btn-'),],
        [sg.Text("取引する金額 [円] ※未指定の場合は満額設定 ")],
        [sg.InputText (key='amount', size=(5, 1),default_text = 70000)],      
        #[sg.Text("ここは出力領域", size=(60,5), values['ConfigName'], values['a1'], values['amount'], )],
        [sg.Text("サンプリング時間")],
        [sg.InputText (key='SamplingTime', size=(5, 1), default_text = 20)],   
        
            ]
            
    layout2 = [
       
        [sg.Checkbox('MACD有効化', key = 'MACD有効化', default=True),],
        [sg.Text("ema1"),sg.Text("ema2"),sg.Text("sma"),sg.Text("duration")],
        [sg.InputText (key='ema1', size=(5, 1)),sg.InputText (key='ema2', size=(5, 1)),sg.InputText (key='sma', size=(5, 1))],
      
        [sg.Checkbox('RSI有効化', key = 'RSI有効化',default=True),],
        [sg.Text("次の値を割ったら売られすぎと判定"),],
        [sg.InputText (key='RSI_min', size=(3, 1),default_text = 30),],
        [sg.Text("次の値を超えたら買われすぎと判定"),],
        [sg.InputText (key='RSI_max', size=(3, 1),default_text = 70),],
     
        [sg.Checkbox('BOLLINGERBAND有効化',key = 'BOLLINGERBAND有効化',default=True),],
        [sg.Radio('1σ（32%）', key = '1σ', group_id='a2',default=False),sg.Radio('2σ（5%）', key = '2σ',group_id='a2',default=True),sg.Radio('3σ（0.3%）', key = '3σ' ,group_id='a2',default=False),], 
       # [sg.InputText (key='sigma', size=(3, 1) ,default_text=2)],
 
          ]
 #0330#####
    layout3 = [
        [sg.Text("注意！アルゴリズムを無効にした場合、下記の設定値は０と設定されます。得点を設定する場合は、アルゴリズム設定タブで、得点を設定したいアルゴリズムに対してチェックを入れて下さい。")],
        [sg.Text("手法/分足"),sg.Text("1分    "),sg.Text("5分  "),sg.Text("  30分   "),sg.Text("  1時間   "),sg.Text("  4時間 "),],
        [sg.Text("MACD"),sg.InputText(key='macd_1minScore', size=(6, 1),default_text=0.5),sg.InputText(key='macd_5minScore', size=(6, 1),default_text=0.5),sg.InputText(key='macd_30minScore', size=(6, 1),default_text=0),sg.InputText(key='macd_1hScore', size=(6, 1),default_text=0),sg.InputText(key='macd_4hScore', size=(6, 1),default_text=0)],#変数名を変える
        [sg.Text("RSI    "),sg.InputText(key='rsi_1minScore', size=(6, 1),default_text=0.5),sg.InputText(key='rsi_5minScore', size=(6, 1),default_text=0.5),sg.InputText(key='rsi_30minScore', size=(6, 1),default_text=0),sg.InputText(key='rsi_1hScore', size=(6, 1),default_text=0),sg.InputText(key='rsi_4hScore', size=(6, 1),default_text=0)],
        [sg.Text("BOLL "),sg.InputText(key='boll_1minScore', size=(6, 1),default_text=0.5),sg.InputText(key='boll_5minScore', size=(6, 1),default_text=0.5),sg.InputText(key='boll_30minScore', size=(6, 1),default_text=0),sg.InputText(key='boll_1hScore', size=(6, 1),default_text=0),sg.InputText(key='boll_4hScore', size=(6, 1),default_text=0)],
        [sg.Text("買い判定合計得点値"),sg.Text("売り判定合計得点値"),],
        [sg.InputText(key='total_buyScore', size=(5, 1),default_text = 0.5),sg.InputText(key='total_sellScore', size=(5, 1),default_text = 2.0),],
          ]
 
    layout4 = [
        [sg.Text("工事中 アルゴリズムの判定順番を設定 （例 : MACD→RSI or RSI→MACD） 工事中 "),],
          ]
 
# 3タブのメイン画面を作成
    Tab3_layout = [
        [sg.TabGroup([[sg.Tab("概要", layout1),
                       sg.Tab("アルゴリズム設定", layout2),
                       sg.Tab("得点・足設定", layout3),
                       sg.Tab("フローチャート設定", layout4)]],
                     
                    ),[sg.Button('やめる'), sg.Button('設定保存') , sg.Button('開始')]
         ]]
 
    Sub_window = sg.Window("取引設定", Tab3_layout)

    return Sub_window


##########################################
####
def save_config():
    
        #f = open(f'{CT.year}年{CT.month}月{CT.day}日{CT.hour}時{CT.minute}分.txt', 'a',encoding='utf-8')
        #取引銘柄の判定
        if values['BTC/JPY'] == True:
            values['coin'] = "btc"#_jpy
        if values['ETC/JPY'] == True:
            values['coin'] = "etc"
        if values['LSK/JPY'] == True:
            values['coin'] = "lsk"
        if values['MONA/JPY'] == True:
            values['coin'] = "mona"
        if values['OMG/JPY'] == True:
            values['coin'] = "omg"
        if values['PLT/JPY'] == True:
            values['coin'] = "plt"
        
        
        #アルゴリズム選択を判定
        if values['MACD有効化'] == False:
          
            values['macd_1minScore'] = 0#0330
            values['macd_5minScore'] = 0
            values['macd_30minScore'] = 0
            values['macd_1hScore'] = 0
            values['macd_4hScore'] = 0
            
        if values['RSI有効化'] == False:
           
            values['rsi_1minScore'] = 0
            values['rsi_5minScore'] = 0
            values['rsi_30minScore'] = 0
            values['rsi_1hScore'] = 0
            values['rsi_4hScore'] = 0
            
        if values['BOLLINGERBAND有効化'] == False:
            
            values['boll_1minScore'] = 0
            values['boll_5minScore'] = 0
            values['boll_30minScore'] = 0
            values['boll_1hScore'] = 0
            values['boll_4hScore'] = 0

        #ボリンジャーバンドの設定について
        if values['1σ'] == True:
            values['sigma'] = 1
        if values['2σ'] == True:
            values['sigma'] = 2
        if values['3σ'] == True:
            values['sigma'] = 3
            
            
        
        if os_name == "Windows":
            print("Hello World for Windows!")   
            with open(fr'C:\Users\たけ\Desktop\チャート\TradeConfig.csv', 'a', newline="", encoding='utf-8')as f:
                writer = csv.writer(f)
                CT = datetime.datetime.today().replace(microsecond=0)
                writer.writerow([fr'{CT.year}年{CT.month}月{CT.day}日{CT.hour}時{CT.minute}分', values['ConfigName'], values['シミュレーションモード'], values['coin'], values['amount'],
                        values['MACD有効化'], 
                        values['ema1'], values['ema2'],values['sma'],
                        
                        values['RSI有効化'], 
                        values['RSI_min'], values['RSI_max'],
                        
                        values['BOLLINGERBAND有効化'], 
                        values['sigma'],
                        
                        #以降、総合得点設定
                        values['total_buyScore'], values['total_sellScore'], "アルゴリズム別得点→",
                        
                        #以降、得点設定
                        values['macd_1minScore'], values['rsi_1minScore'], values['boll_1minScore'],           
                        values['macd_5minScore'], values['rsi_5minScore'], values['boll_5minScore'],
                        values['macd_30minScore'], values['rsi_30minScore'], values['boll_30minScore'],
                        values['macd_1hScore'], values['rsi_1hScore'], values['boll_1hScore'],
                        values['macd_4hScore'], values['rsi_4hScore'], values['boll_4hScore'],
                        ])
        
            f.close()
                
        elif os_name == "Darwin":
            print("Hello World for MacOS!")
            with open(f'/Users/mac/Desktop/チャート/TradeConfig.csv', 'a', newline="", encoding='utf-8')as f:
                writer = csv.writer(f)
                CT = datetime.datetime.today().replace(microsecond=0)
                writer.writerow([f'{CT.year}年{CT.month}月{CT.day}日{CT.hour}時{CT.minute}分', values['ConfigName'], values['シミュレーションモード'], values['coin'], values['amount'],
                        values['MACD有効化'], 
                        values['ema1'], values['ema2'],values['sma'],
                        
                        values['RSI有効化'], 
                        values['RSI_min'], values['RSI_max'],
                        
                        values['BOLLINGERBAND有効化'], 
                        values['sigma'],
                        
                        #以降、総合得点設定
                        values['total_buyScore'], values['total_sellScore'], "アルゴリズム別得点→",
                        
                        #以降、得点設定
                        values['macd_1minScore'], values['rsi_1minScore'], values['boll_1minScore'],           
                        values['macd_5minScore'], values['rsi_5minScore'], values['boll_5minScore'],
                        values['macd_30minScore'], values['rsi_30minScore'], values['boll_30minScore'],
                        values['macd_1hScore'], values['rsi_1hScore'], values['boll_1hScore'],
                        values['macd_4hScore'], values['rsi_4hScore'], values['boll_4hScore'],
                        
                        ])
        
            f.close()
        
                  
        print("保存しました")
        #0330############
        Config = pd.Series({"ConfigName":values['ConfigName'], "シミュレーションモード":values['シミュレーションモード'],"coin":values['coin'], "amount": values['amount'], "MACD有効化":values['MACD有効化'], "ema1": values['ema1'], "ema2":values['ema2'], "sma":values['sma'],"RSI有効化":values['RSI有効化'], "RSI_min":values['RSI_min'], "RSI_max":values['RSI_max'],"BOLLINGERBAND有効化":values['BOLLINGERBAND有効化'], "sigma":values['sigma'],"total_buyScore":values['total_buyScore'], "total_sellScore":values['total_sellScore'],
        
        #"macd_1minScore":values['macd_1minScore'],"macd_5minScore":values['macd_5minScore'], "macd_30minScore":values['macd_30minScore'], "macd_1hScore":values['macd_1hScore'], "macd_4hScore":values['macd_4hScore'],
        #"rsi_1minScore":values['rsi_1minScore'],"rsi_5minScore":values['rsi_5minScore'], "rsi_30minScore":values['rsi_30minScore'], "rsi_1hScore":values['rsi_1hScore'], "rsi_4hScore":values['rsi_4hScore'],
        #"boll_1minScore":values['boll_1minScore'],"boll_5minScore":values['boll_5minScore'], "boll_30minScore":values['boll_30minScore'],"boll_1hScore": values['boll_1hScore'], "boll_4hScore":values['boll_4hScore'],
        
        "macd_1minScore":values['macd_1minScore'], "rsi_1minScore":values['rsi_1minScore'], "boll_1minScore":values['boll_1minScore'],           
        "macd_5minScore":values['macd_5minScore'], "rsi_5minScore":values['rsi_5minScore'], "boll_5minScore":values['boll_5minScore'],
        "macd_30minScore":values['macd_30minScore'], "rsi_30minScore":values['rsi_30minScore'], "boll_30minScore":values['boll_30minScore'],
        "macd_1hScore":values['macd_1hScore'], "rsi_1hScore":values['rsi_1hScore'], "boll_1hScore":values['boll_1hScore'],
        "macd_4hScore":values['macd_4hScore'], "rsi_4hScore":values['rsi_4hScore'], "boll_4hScore":values['boll_4hScore'],
        
        "SamplingTime":values['SamplingTime']}) 
        print(Config)
        return Config
    
window = make_main()



#メイン、サブ共通
while True:
    event, values = window.read()
 
# ×ボタンが押された場合
    if event == sg.WIN_CLOSED:
        break
 
# ＋ボタンが押された場合
    if event == "-ADD-":
        window = make_sub()
 
# 初期設定ボタンが押された場合
    if event == "-APIConfig-":
        #window = make_config()##工事中
        print('初期設定')
              
# やめるボタンが押された場合
    if event == "やめる":
        window.close()
        window = make_main()
 
# 設定保存ボタンが押された場合
    if event == "設定保存":
        save_config()
        #window.close()
        #window = make_main()
 
# 開始ボタンが押された場合
    if event == "開始":
# 保存し、サブウィンドウを閉じて、mai.pyを実行

        #設定された値をmainに渡す
        Config = save_config()
 
        print('取引開始1')
        #window.close()
        #window = make_main()
        gc.collect() 
        window.close()
        
        import main
        #exec(open("./main.py").read())
        #window.close()
        #break
        
 
window.close()
