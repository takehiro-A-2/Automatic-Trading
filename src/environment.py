import os
from dotenv import load_dotenv
import UI
# .envファイルの内容を読み込見込む
load_dotenv()

##############################
# 共通変数
##############################

# 計測間隔
INTERVAL = os.environ.get('INTERVAL')

# 通貨
#COIN = os.environ.get('COIN')
COIN = UI.Config['coin']
PAIR = str(COIN) + '_jpy'

# 購入金額
#AMOUNT = os.getenv('AMOUNT')
AMOUNT= float(UI.Config['amount'])

#BUYCOINAMOUNT
BUY_COIN_AMOUNT = None


# 注文ID
order_id = None
# 購入金額
market_buy_amount = None
# 売却金額
market_sell_amount = None

# 注文キャンセルID
order_id_cancel = None

#直近の取引の買値と売値
buy_price:int = 0
sell_price:int = 0

# 利益
#PROFIT = os.environ.get('PROFIT')                                           
profit:int = 0

# シミュレーション用通貨
simulation_jpy = float(UI.Config['amount'])
simulation_coin = float(0)


#########################使わないメゾット##################################

# シミュレーションモード
SIMULATION = os.getenv('SIMULATION')
simulation = False if SIMULATION is None or SIMULATION == '' or SIMULATION == 'false' else True

# アルゴリズム
ALGORITHM = os.environ.get('ALGORITHM')

