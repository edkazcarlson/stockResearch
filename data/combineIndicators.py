import pandas as pd
stockDataPath = 'stockDataIndicators.csv'
sentimentPath = 'sentimentIndicators.csv'
econimicDataPath = 'economicIndicators.csv'
destPath = 'masterDF.csv'

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
												'tmmrwChngAsPerc': 'float64',
												'zScoreOfChangeTmmrw': 'float64',
												'percentChangeInFiveDays': 'float64',
												'thisDayZScore': 'float64',
												'thisDayAveragePercentChange': 'float64',
												'thisDayPercentChangeStdev': 'float64'})
sentDF = pd.read_csv(sentimentPath, dtype = {'sent': 'float64'})
econimicDF = pd.read_csv(econimicDataPath)
masterDF = pd.merge(masterDF, sentDF, right_on = 'Date', left_on = 'Date')
masterDF.dropna(inplace = True)
sentDF = None
masterDF = pd.merge(masterDF, econimicDF, right_on = 'Date', left_on = 'Date')
masterDF.to_csv(destPath)