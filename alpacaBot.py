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
import threading

class tradingBot(threading.Thread):
	def __init__(self, api, strategy, accountRatio):
		self.api = api
		self.strategy = strategy
		self.accountRatio = accountRatio
	
	class Choice(Enum):
		LONG = 0
		SHORT = 1
		HOLD = 2

	#tobuy and toSell are in format of stock ticker -> agreement
	#returns toBuy and toSell in format ticker -> amount to buy/sell, price
	def appendAmountWithPrice(toBuy, toSell, votePercentage):
		account = self.api.get_account()
		buyingPower = account.buying_power * self.accountRatio
		longBudget = 0.7 * buyingPower
		shortBudget = (1 - longRatio) * buyingPower
		budgets = [longBudget, shortBudget]
		dictList = [toBuy, toSell]
		
		for index in range(len(dictList)):
			orderDict = dictList[index]
			budget = budgets[index]
			totalAgreement = 0
			for stock in orderDict:#summing agreement
				totalAgreement += orderDict[stock]
			
			for stock in orderDict:#putting amount and price onto dict
				barset = api.get_barset(stock, 'day', limit=1)
				stockPrice = barset[stock].c
				stockBudget = budget * orderDict[stock] / totalAgreement
				amountToBuy = stockBudget / stockPrice
				orderDict[stock] = [amountToBuy, stockPrice]
			


	#get the data of the stock and generate the values to feed into the strategy forest
	def getData(stock):
		barset = api.get_barset(stock, 'day', limit=10)
		stockBars = barset[stock]
		valuesList = []
		#calculate and append the values needed to valuesList
		tenDayVolume = [x.v for x in stockBars]
		volumeMean = sum(tenDayVolume)/len(tenDayVolume)
		VolumeZScoreTenDay = 0
		if statistics.stdev(tenDayVolume) != 0:
			VolumeZScoreTenDay = (stockBars[0].v - volumeMean) / statistics.stdev(tenDayVolume)
		highVsLowPerc = (stockBars[0].h - stockBars[0].l) / stockBars[0].l
		dayPercentChange = (stockBars[0].c - stockBars[0].o)/stockBars[0].o
		
		fiveDayAverage = (stockBars[0].c + stockBars[1].c + stockBars[2].c + stockBars[3].c + stockBars[4].c) / 5
		tenDayAverage = sum([x.c for x in stockBars])/10
		fiveVsTenDayAverage = (fiveDayAverage - tenDayAverage) /tenDayAverage
		
		fiveDayWeightedAverage = sum([stockBars[x].c * (5 - x) for x in range(5)])/15
		tenDayWeightedAverage = sum([stockBars[x].c * (10 - x) for x in range(10)])/5
		fiveVSTenDayWeightedAverage = (fiveDayWeightedAverage - tenDayWeightedAverage) /tenDayWeightedAverage
		
		fiveDaySlopeChange = (stockBars[0].c - stockBars[4].o ) / 5
		tenDaySlopeChange = (stockBars[0].c - stockBars[9].o ) / 10
		fiveVsTenDaySlopeChange = fiveDaySlopeChange - fiveDaySlopeChange
		
		valuesList.append(VolumeZScoreTenDay)
		valuesList.append(highVsLowPerc)
		valuesList.append(dayPercentChange)
		valuesList.append(fiveVSTenDayWeightedAverage)
		valuesList.append(fiveVsTenDaySlopeChange)
		valuesList.append(fiveVsTenDayAverage)
		return valuesList
		

	#decide which stocks to trade and how much, use appendAmountWithPrice
	def chooseWhichToTrade():
		#get stock data from the past day for stocks in my universe
		#get the top 10%, bottom 5%
		#sell bottom 5% of stocks, then buy the top 10% based on appendAmountWithPrice
		
		#returns choice, % of votes for that choice, -1 if hold
		def choose(votePercentage):
			indices = [i for i, x in enumerate(votePercentage) if x == max(votePercentage)]
			voteSum = sum(votePercentage)
			if len(indices) == 1:
				return Choice(indices[0]), indices[0] / voteSum 
			else:
				return Choice.HOLD, -1
			
		tommorowZScorePredictorLoc = ''
		fiveDayPredictorLoc = ''
		toBuy = dict()
		toSell = dict()
		
		for stock in universe: #decide whether to buy/sell and how much along with stoploss/limit price
			stockData = getData(stock)
			votePercentage = self.strategy.predictProba(stockData)
			thisChoice, agreement = choose(votePercentage)
			if thisChoice is Choice.LONG:
				toBuy[stock] = [agreement]
			elif thisChoice is Choice.SHORT:
				toSell[stock] = [agreement]
			else:#decision was to hold
				pass
		appendAmountWithPrice(toBuy, toSell)
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
				order_class = 'bracket',
				stop_loss=dict(
					stop_price = toBuy[symbol][1] * stopLossRatio),
				take_profit = dict(
					limit_price = toBuy[symbol][1] * takeProftRatio)
			)

	#continuously runs	
	def run(self):
		api = self.api
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

