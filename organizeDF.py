import os
import pandas as pd
import statistics
import numpy as np


def genXDayAverage(df, days, tag):
	toReturn = np.array([0] * df.shape[0])
	toReturn = pd.Series(toReturn, dtype = 'float64')
	for x in range(days):
		shiftedSeries = df[tag]
		toReturn = toReturn.add(shiftedSeries)
	return toReturn.div(days)

def stdDevLastXDays(df, days,tag):
	toReturn = []
	pastXDayList = [np.nan] * days
	for _,item in df[tag].items():
		pastXDayList.append(item)
		pastXDayList.pop(0)
		try:
			toReturn.append(statistics.stdev(pastXDayList))
		except:
			toReturn.append(np.nan)
	toReturn = pd.Series(toReturn)
	return toReturn

def bBandFn(closeVal, upperBandVal, lowerBandVal):
	return 'Over' if closeVal > upperBandVal else 'Under' if closeVal < lowerBandVal else 'Within' 
	
#from https://www.kaggle.com/borismarjanovic/price-volume-data-for-all-us-stocks-etfs 
filePath = 'price-volume-data-for-all-us-stocks-etfs/Stocks' #using the 1500 stocks with the most data on them
fileList = os.listdir(filePath)
 
counter = 0
for file in fileList:
	if counter % 50 == 0:
		print(counter)
	print(file)
	counter += 1 
	df = pd.read_csv(filePath + '/' + file, usecols = ['Date','Open','High','Low','Close','Volume'], parse_dates = ['Date'])
	df = df[df['Date'] > np.datetime64('2010-01-01')]	
	df.reset_index(inplace = True)
	tickerSymbol = file.split('.us.txt')[0].upper()
	rowCount = df.shape[0]
	emptyRow = [0.0] * rowCount
	df = df.assign(VolumeZScoreTenDay = emptyRow, highVsLowPerc = emptyRow, dayPercentChange = emptyRow, ticker = [tickerSymbol]* df.shape[0], 
				   fiveDayAverage = emptyRow, tenDayAverage = emptyRow, fiveDayWeightedAverage = emptyRow, tenDayWeightedAverage = emptyRow,
				   fiveVSTenDayWeightedAverage = emptyRow, fiveDaySlopeChange = emptyRow, tenDaySlopeChange = emptyRow, fiveVsTenDaySlopeChange = emptyRow,
				   fiveVsTenDayAverage = emptyRow, MACD = emptyRow, bPercent = emptyRow,
				   tmmrwChngAsPerc = emptyRow, zScoreOfChangeTmmrw = emptyRow, percentChangeInFiveDays = emptyRow)
	volCounter = 0
	tenDayVolume = []
	volumeZList = []
	for label, item in df['Volume'].items():
		volCounter += 1
		tenDayVolume.append(item)
		if volCounter >= 10:
			volumeZList.append((item - (sum(tenDayVolume)/len(tenDayVolume)))/statistics.stdev(tenDayVolume))
			tenDayVolume.pop(0)
		else:
			volumeZList.append(np.nan)
	df['VolumeZScoreTenDay'] = volumeZList
	df['highVsLowPerc'] = ((df['High'] - df['Low']).div(df['Low']))
	df['dayPercentChange'] = ((df['Close'] - df['Open']).div(df['Open']))
	df['fiveDayAverage'] = genXDayAverage(df, 5, 'Close')
	df['tenDayAverage'] = genXDayAverage(df, 10, 'Close')
	df['fiveDayWeightedAverage'] = (((df['Close']*5) + (df['Close'].shift(1) * 4) + (df['Close'].shift(2) * 3) + 
									 (df['Close'].shift(3) * 2) + (df['Close'].shift(4))).div(15))
	df['tenDayWeightedAverage'] = (((df['Close']*10) + (df['Close'].shift(1) * 9) + (df['Close'].shift(2) * 8) + 
									 (df['Close'].shift(3) * 7) + (df['Close'].shift(4) * 6) + (df['Close'].shift(5) * 5)+
									 (df['Close'].shift(7) * 3)+ (df['Close'].shift(8) * 2) + (df['Close'].shift(9))).div(55))
	df['fiveVSTenDayWeightedAverage'] = (df['fiveDayWeightedAverage'] - df['tenDayWeightedAverage']).div(df['tenDayWeightedAverage'])
	df['fiveDaySlopeChange'] = ((df['Close']  - df['Open'].shift(4)).div(5))
	df['tenDaySlopeChange'] = ((df['Close']  - df['Open'].shift(9)).div(10))	
	df['fiveVsTenDaySlopeChange'] = (df['fiveDaySlopeChange'] - df['tenDaySlopeChange'])
	df['fiveVsTenDayAverage'] = (df['fiveDayAverage'] - df['tenDayAverage']).div(df['tenDayAverage'])
	df['MACD'] = (genXDayAverage(df, 12, 'Close') - genXDayAverage(df, 26, 'Close'))
	days = 25
	Std = stdDevLastXDays(df, days,'Close')
	Average = genXDayAverage(df, days, 'Close')
	upperBand = ((Std).multiply(2) + Average)
	lowerBand = ((Std).multiply(-2) + Average)
	bPercent = []
	for close, upper, lower in zip (df['Close'], upperBand, lowerBand):
		bPercent.append((close - lower)/(upper - lower))
	df['bPercent'] = bPercent		
	df['tmmrwChngAsPerc'] = ((df['Close'].shift(-1) - df['Open'].shift(-1)).div(df['Open'].shift(-1)))
	stdDevOfChangePercent = pd.Series.std(df['tmmrwChngAsPerc'])
	meanOfChangePercent = pd.Series.mean(df['tmmrwChngAsPerc'])
	df['zScoreOfChangeTmmrw'] = (df['tmmrwChngAsPerc'] - meanOfChangePercent).div(stdDevOfChangePercent)
	df['percentChangeInFiveDays'] = ((df['Close'].shift(-5) - df['Close']).div(df['Close']))
	df.dropna(inplace = True)
	if counter == 1:
		df.to_csv('masterDF.csv', index = False)
	else:
		df.to_csv('masterDF.csv', mode = 'a', header = False,index = False)

		
sectorDataPath = 'nyse/securities.csv'
sectorDataDF = pd.read_csv(sectorDataPath)#,usecols = ['Ticker symbol','GICS Sector','GICS Sub Industry']).set_index('Ticker symbol')
masterDF = pd.read_csv('masterDF.csv').set_index(['ticker','Date'])
print(sectorDataDF.head(3))

combinedDF = pd.merge(masterDF, sectorDataDF, right_on = 'ticker', left_on = 'ticker', how = 'left')
combinedDF.dropna(inplace = True)
combinedDF.to_csv('combinedDF.csv', index = False)
print('finished cleaning')
