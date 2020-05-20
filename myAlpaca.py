import alpaca_trade_api as tradeapi
import pandas as pd
import statistics
import sys
import time
import pickle
from enum import Enum
import json
from datetime import datetime, timedelta
from pytz import timezone
import alpacaBot

if __name__ == "__main__":
	zStrategy = pickle.load(open('zScorePredictor.pkl','rb'))
	fiveDayStrategy = pickle.load(open('fiveDayChangePredictor.pkl','rb'))
	baseURL = 'https://paper-api.alpaca.markets'
	apikey = ''
	secretKey = ''
	with open('config/alpacaKeys.json', 'r') as f:
		data = json.load(f)
		apikey = data['APIKEY']
		secretKey = data['SECRETKEY']

	api = tradeapi.REST(apikey, secretKey, baseURL)
	zBot = alpacaBot.tradingBot(api, zStrategy, .5)
	fiveDayBot = alpacaBot.tradingBot(api, fiveDayStrategy, .5)
	#run(api)