import os
import pandas as pd
#from https://www.kaggle.com/borismarjanovic/price-volume-data-for-all-us-stocks-etfs removing all stocks with less than 1 year of data
filePath = 'price-volume-data-for-all-us-stocks-etfs/Stocks'
fileList = os.listdir(filePath)
masterDF = pd.DataFrame({'Date': [],
						'Open': [],
						'High': [],
						'Low': [],
						'Close': [],
						'Volume': [],
						'VolumeZScore': [],
						'highVsLowPerc': [],
						'dayPercentChange': [],
						'ticker': [],
						'fiveDayAverage': [],
						'tenDayAverage': [],
						'fiveDayWeightedAverage': [],
						'tenDayWeightedAverage': [],
						'fiveDaySlopeChange': [],
						'tenDaySlopeChange': [],
						'fiveVsTenDaySlopeChange': [],
						'fiveVsTenDayAverage': [],
						'tmmrwChngAsPerc': [],
						'zScoreOfChangeTmmrw': [],
						'percentChangeInFiveDays': []},
				  index=[])   
counter = 0
for file in fileList:
	if counter % 50 == 0:
		print(counter)
	counter += 1 
	if counter > 3:
		break
	try:
		df = pd.read_csv(filePath + '/' + file, parse_dates = True, usecols = ['Date','Open','High','Low','Close','Volume'])
		tickerSymbol = file.split('.us.txt')[0]
		rowCount = df.shape[0]
		emptyRow = [0.0] * rowCount
		df = df.assign(VolumeZScore = emptyRow, highVsLowPerc = emptyRow, dayPercentChange = emptyRow, ticker = [tickerSymbol]* df.shape[0], 
					   fiveDayAverage = emptyRow, tenDayAverage = emptyRow, fiveDayWeightedAverage = emptyRow, tenDayWeightedAverage = emptyRow,
					   fiveDaySlopeChange = emptyRow, tenDaySlopeChange = emptyRow, fiveVsTenDaySlopeChange = emptyRow,
					   fiveVsTenDayAverage = emptyRow, tmmrwChngAsPerc = emptyRow, zScoreOfChangeTmmrw = emptyRow, 
					   percentChangeInFiveDays = emptyRow)
		stdDevOfVolume = pd.Series.std(df['Volume'])
		meanOfVolume = pd.Series.mean(df['Volume'])
		df['VolumeZScore'] = (df['Volume'] - meanOfVolume).div(stdDevOfVolume)
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
		print(df.head())
		masterDF = pd.concat([masterDF, df])
	except:
		print("error for: ", file)
print('finished cleaning')
masterDF.to_csv('masterDF.csv', index=False) 