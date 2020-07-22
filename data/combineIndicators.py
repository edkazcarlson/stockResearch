import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from datetime import date

stockDataPath = 'stockDataIndicators.csv'
sentimentPath = 'sentimentIndicators.csv'
econimicDataPath = 'economicIndicators.csv'
tempPath = 'temp.csv'
smallPath = 'filtered.csv'
def partOne():
	masterDF = pd.read_csv(stockDataPath, dtype = {'Open': 'float64', 
													'High': 'float64',
													'Low': 'float64',
													'Close': 'float64',
													'Volume': 'float64',
													'VolumeZScoreTenDay': 'float64',
													'highVsLowPerc': 'float64',
													'dayPercentChange': 'float64',
													'fiveDayAverage': 'float64',
													'tenDayAverage': 'float64',
													'fiveDayWeightedAverage': 'float64',
													'tenDayWeightedAverage': 'float64',
													'fiveVSTenDayWeightedAverage': 'float64',
													'fiveDaySlopeChange': 'float64',
													'tenDaySlopeChange': 'float64',
													'fiveVsTenDaySlopeChange': 'float64',
													'fiveVsTenDayAverage': 'float64',
													'MACD': 'float64',
													'bPercent': 'float64',
													'typPrice': 'float64',
													'averageUp' :'float64',
													'averageDown' :'float64',
													'totalVolumeOfTheDay': 'int64',
													'WilliamsR': 'float64',
													'vsMarketPerformance': 'float64',
													'rsi' :'float64',
													'tmmrwChngAsPerc': 'float64',
													'zScoreOfChangeTmmrw': 'float64',
													'percentChangeInFiveDays': 'float64',
													'thisDayZScore': 'float64',
													'thisDayAveragePercentChange': 'float64',
													'thisDayPercentChangeStdev': 'float64'}, parse_dates = ['Date'])
	masterDF.drop(columns=['thisDayAveragePercentChange', 'thisDayPercentChangeStdev',
			'fiveDayWeightedAverage', 'tenDayWeightedAverage', 'fiveDaySlopeChange', 'tenDaySlopeChange', 
			'High', 'Low', 'Open', 'Close', 'Volume', 'fiveDayAverage', 'tenDayAverage', 'tommorowVSMarketPerformance'], inplace = True)
	masterDF.dropna(inplace = True)
	sentDF = pd.read_csv(sentimentPath, dtype = {'sent': 'float64', 
												'titleSent': 'float64', 
												'articleSent': 'float64', 
												'titleSentChangeSinceYesterday': 'float64', 
												'articleSentChangeSinceYesterday' : 'float64', 
												'titleSentbPercent': 'float64', 
												'articleSentbPercent': 'float64'}, parse_dates = ['Date'])
	masterDF = pd.merge(masterDF, sentDF, right_on = 'Date', left_on = 'Date')
	masterDF.dropna(inplace = True)
	sentDF = None
	econimicDF = pd.read_csv(econimicDataPath, parse_dates = ['Date'])
	econimicDF.drop(columns = ['DPRIMEfiveVsTenTickAverage', 'DPRIMEbPercent'], inplace = True)
	masterDF = pd.merge(masterDF, econimicDF, right_on = 'Date', left_on = 'Date')
	for col in masterDF.columns:
		print(col)
	masterDF.to_csv(tempPath, index = False)

def partTwo():
	firstTime = True
	for chunk in pd.read_csv(tempPath, chunksize = 15000, parse_dates = ['Date']):
		chunk.dropna(inplace = True)
		chunk['dateOfYear'] = chunk.apply(lambda row: (date(row['Date'].year, row['Date'].month, row['Date'].day) - date(row['Date'].year, 1, 1)).days, axis = 1)
		if firstTime:
			chunk.to_csv(smallPath, index = False)
			firstTime = False
		else:
			chunk.to_csv(smallPath, mode = 'a', header = False,index = False)
partOne()
partTwo()
