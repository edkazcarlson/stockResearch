import os
import pandas as pd
import statistics
import numpy as np
#from https://www.kaggle.com/borismarjanovic/price-volume-data-for-all-us-stocks-etfs removing all stocks with less than 1 year of data
filePath = 'price-volume-data-for-all-us-stocks-etfs/Stocks'
fileList = os.listdir(filePath)
 
counter = 0
for file in fileList:
	if counter % 50 == 0:
		print(counter)
	counter += 1 
	try:
		df = pd.read_csv(filePath + '/' + file, usecols = ['Date','Open','High','Low','Close','Volume'], parse_dates = ['Date'])
		tickerSymbol = file.split('.us.txt')[0]
		rowCount = df.shape[0]
		emptyRow = [0.0] * rowCount
		df = df.assign(VolumeZScoreTenDay = emptyRow, highVsLowPerc = emptyRow, dayPercentChange = emptyRow, ticker = [tickerSymbol]* df.shape[0], 
					   fiveDayAverage = emptyRow, tenDayAverage = emptyRow, fiveDayWeightedAverage = emptyRow, tenDayWeightedAverage = emptyRow,
					   fiveVSTenDayWeightedAverage = emptyRow, fiveDaySlopeChange = emptyRow, tenDaySlopeChange = emptyRow, fiveVsTenDaySlopeChange = emptyRow,
					   fiveVsTenDayAverage = emptyRow, tmmrwChngAsPerc = emptyRow, zScoreOfChangeTmmrw = emptyRow, 
					   percentChangeInFiveDays = emptyRow)
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
		df['fiveDayAverage'] = ((df['Close'] + df['Close'].shift(1) + df['Close'].shift(2) + df['Close'].shift(3) + df['Close'].shift(4)).div(5))
		df['tenDayAverage'] = ((df['Close'] + df['Close'].shift(1) + df['Close'].shift(2) + df['Close'].shift(3) + df['Close'].shift(4) + 
							   (df['Close'].shift(5) + df['Close'].shift(6) + df['Close'].shift(7) + df['Close'].shift(8) + df['Close'].shift(9)).div(10)))
		df['fiveDayWeightedAverage'] = (((df['Close']*5) + (df['Close'].shift(1) * 4) + (df['Close'].shift(2) * 3) + 
										 (df['Close'].shift(3) * 2) + (df['Close'].shift(4))).div(15))
		df['tenDayWeightedAverage'] = (((df['Close']*10) + (df['Close'].shift(1) * 9) + (df['Close'].shift(2) * 8) + 
										 (df['Close'].shift(3) * 7) + (df['Close'].shift(4) * 6) + (df['Close'].shift(5) * 5)+
										 (df['Close'].shift(7) * 3)+ (df['Close'].shift(8) * 2) + (df['Close'].shift(9))).div(55))
		df['fiveDaySlopeChange'] = ((df['Close']  - df['Open'].shift(4)).div(5))
		df['tenDaySlopeChange'] = ((df['Close']  - df['Open'].shift(9)).div(10))	
		df['fiveVsTenDaySlopeChange'] = (df['fiveDaySlopeChange'] - df['tenDaySlopeChange'])
		df['fiveVsTenDayAverage'] = (df['fiveDayAverage'] - df['tenDayAverage'])
		df['tmmrwChngAsPerc'] = ((df['Close'].shift(-1) - df['Open'].shift(-1)).div(df['Open'].shift(-1)))
		stdDevOfChangePercent = pd.Series.std(df['tmmrwChngAsPerc'])
		meanOfChangePercent = pd.Series.mean(df['tmmrwChngAsPerc'])
		df['zScoreOfChangeTmmrw'] = (df['tmmrwChngAsPerc'] - meanOfChangePercent).div(stdDevOfChangePercent)
		df['percentChangeInFiveDays'] = ((df['Close'].shift(-5) - df['Close']).div(df['Close']))
		df.dropna(inplace = True)
		df = df[df['Date'] > np.datetime64('2010-01-01')]
		if counter == 1:
			df.to_csv('masterDF.csv', index = False)
		else:
			df.to_csv('masterDF.csv', mode = 'a', index = False)
	except:
		print("error for: ", file)
print('finished cleaning')