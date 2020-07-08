import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from datetime import date

stockDataPath = 'stockDataIndicators.csv'
sentimentPath = 'sentimentIndicators.csv'
econimicDataPath = 'economicIndicators.csv'
destPath = 'masterDF.csv'
smallPath = 'filtered.csv'

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
												'averageUp' :'float64',
												'averageDown' :'float64',
												'totalVolumeOfTheDay': 'int64',
												'rsi' :'float64',
												'tmmrwChngAsPerc': 'float64',
												'zScoreOfChangeTmmrw': 'float64',
												'percentChangeInFiveDays': 'float64',
												'thisDayZScore': 'float64',
												'thisDayAveragePercentChange': 'float64',
												'thisDayPercentChangeStdev': 'float64'}, parse_dates = ['Date'])
sentDF = pd.read_csv(sentimentPath, dtype = {'sent': 'float64'}, parse_dates = ['Date'])
econimicDF = pd.read_csv(econimicDataPath, parse_dates = ['Date'])
masterDF = pd.merge(masterDF, sentDF, right_on = 'Date', left_on = 'Date')
masterDF.dropna(inplace = True)
sentDF = None
masterDF = pd.merge(masterDF, econimicDF, right_on = 'Date', left_on = 'Date')
masterDF.dropna(inplace = True)
masterDF['dateOfYear'] = masterDF.apply(lambda row: (date(row['Date'].year, row['Date'].month, row['Date'].day) - 	date(row['Date'].year, 1, 1)).days, axis = 1)
masterDF.to_csv(destPath, index = False)
masterDF.drop(columns=['tmmrwChngAsPerc', 'Date', 'thisDayAveragePercentChange', 'thisDayPercentChangeStdev',
        'fiveDayWeightedAverage', 'tenDayWeightedAverage', 'fiveDaySlopeChange', 'tenDaySlopeChange', 
        'High', 'Low', 'Open', 'Close', 'Volume', 'fiveDayAverage', 'tenDayAverage', 'tommorowVSMarketPerformance'], inplace = True)
masterDF.to_csv(smallPath, index = False)

