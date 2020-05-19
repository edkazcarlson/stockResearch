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

class Choice(Enum):
	LONG = 0
	SHORT = 1
	HOLD = 2

#use account.buying_power https://alpaca.markets/docs/api-documentation/how-to/account/ and votes from the randomforest with predictProba
#to get amount to purchase 
def amountWithPrice(symbol, votePercentage):
	stopLossPercent = 0.03

#get the data to feed into the forest from the stock ticker
def getData(stock):
	barset = api.get_barset(stock, 'day', limit=10)
	aapl_bars = barset[stock]
	valuesList = []
	#calculate and append the values needed to valuesList
	return valuesList
	

#decide which stocks to trade and how much, use amountWithPrice
def chooseWhichToTrade():
	#get stock data from the past day for stocks in my universe
	#get the top 10%, bottom 5%
	#sell bottom 5% of stocks, then buy the top 10% based on amountWithPrice
	def choose(votePercentage):
		indices = [i for i, x in enumerate(votePercentage) if x == max(votePercentage)]
		if len(indices) == 1:
			return Choice(indices[0])
		else:
			return Choice.HOLD
		
	tommorowZScorePredictorLoc = ''
	fiveDayPredictorLoc = ''
	tommorowZScorePredictor = open(tommorowZScorePredictorLoc, 'rb')
	fiveDayPredictor = open(fiveDayPredictorLoc, 'rb')
	toBuy = dict()
	toSell = dict()
	
	for stock in universe: #decide whether to buy/sell and how much along with stoploss/limit price
		stockData = getData(stock)
		votePercentage = tommorowZScorePredictor.predictProba(stockData)
		thisChoice = choose(votePercentage)
		if thisChoice is Choice.LONG:
			toBuy[stock] = []
		elif thisChoice is Choice.SHORT:
			toSell[stock] = []
		else:#decision was to hold
			pass
	return toBuy, toSell
	
#dict of symbol -> amount, price for toBuy
#dict of symbol -> amount, price for toSell
def trade(toBuy, toSell):
	takeProftRatio = 1.03
	stopLossRatio = .97
	for symbol in toSell:
		api.submit_order(
			symbol=symbol,
			qty=toSell[symbol][0],
			side='sell',
			type='market',
			time_in_force='day',
			order_class='bracket',
			stop_loss = dict(
				stop_price = toSell[symbol][1] * takeProftRatio),
			take_profit = dict(
				limit_price = toSell[symbol][1] * stopLossRatio)
		)

	for symbol in toBuy:
		api.submit_order(
			symbol=symbol,
			qty=toBuy[symbol][0],
			side='buy',
			type='market',
			time_in_force='day',
			stop_loss=dict(
				stop_price = toBuy[symbol][1] * stopLossRatio)
			take_profit = dict(
				limit_price = toSell[symbol][1] * takeProftRatio)
		)

#continuously runs	
def run(api):
	cycle = 1
	while True:
		clock = api.get_clock()
		tradedToday = False
		toBuy = None
		toSell = None
		if clock.is_open: #if can trade
			if not tradedToday: #but have not traded
				if toBuy == None or toSell == None:#if script was started mid-trading day
					toBuy, toSell = chooseWhichToTrade()
				time_after_open = clock.next_open - clock.timestamp
				#trade a min after market opens
				if time_after_open.seconds >= 60:
					trade(toBuy, toSell)
					tradedToday = True
					toBuy = None
					toSell = None
			else:
				if cycle % 10 == 0:
					print("Already traded today, waiting for next market day...")
					cycle = 1
		else: #still waiting for market open
			if toBuy == None or toSell == None:
				toBuy, toSell = chooseWhichToTrade()
			if cycle % 10 == 0:
				print("Waiting for next market day...")
				cycle = 1
		time.sleep(30)
		cycle+=1
		
if __name__ == "__main__":
	baseURL = 'https://paper-api.alpaca.markets'
	apikey = ''
	secretKey = ''
	with open('config/alpacaKeys.json', 'r') as f:
		data = json.load(f)
		apikey = data['APIKEY']
		secretKey = data['SECRETKEY']

	api = tradeapi.REST(apikey, secretKey, baseURL)
	
	#run(api)