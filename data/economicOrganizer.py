import os
import pandas as pd
import statistics
import numpy as np
import json
import requests
from textblob import TextBlob
import datetime
import multiDayAnalysisTools

os.chdir("..")
parentFilePath = os.path.abspath(os.curdir)
apiKey = ''
with open(parentFilePath + '/config/fredKeys.json', 'r') as f:
	data = json.load(f)
	apiKey = data['APIKEY']
urlRoot = 'https://api.stlouisfed.org/fred/series/observations?'
seriesOfInterest = ['DTWEXAFEGS','DPRIME', 'TOTCI', 'UNRATE', 'CONSUMER','BUSLOANS','CCLACBW027SBOG','STLFSI2', 'PRS85006092', 'TCU', 'BOPGSTB', 'CPIAUCSL',
'SFTPINDM114SFRBSF', 'WALCL', 'M1', 'GOLDAMGBD228NLBM', 'PCEC96', 'DGS30', 'DGS2', 'WPU0911', 'DJIA', 'SP500', 'DEXCHUS', 'DEXUSUK', 'NASDAQCOM', 'WILL5000PR', 'NASDAQ100',
'DEXSZUS', 'DEXJPUS']
dateRange = np.arange('2010-01-01', '2020-05-26', dtype='datetime64[D]')
dateRange = {'Date': dateRange}
dateDF = pd.DataFrame(data = dateRange)
seriesDFList= []
for series in seriesOfInterest:
	url = urlRoot + 'series_id='+ series + '&api_key='+ apiKey + '&file_type=json'
	resp = requests.get(url)
	obs = resp.json()['observations']
	dateList = [x['date'] for x in obs]
	valList = [x['value'] for x in obs]
	valueLabel = series + 'Value'
	newDF = {'Date': dateList, valueLabel: valList}
	newDF = pd.DataFrame(data = newDF)
	newDF['Date'] = pd.to_datetime(newDF['Date'])
	
	newDF.replace(['.'], np.nan, inplace = True)
	newDF.fillna(method = 'ffill', inplace = True)
	newDF[valueLabel] = newDF[valueLabel].astype('float64')
	
	newDF[series + 'lastChangeP'] = (newDF[valueLabel] - newDF[valueLabel].shift(1)).div(newDF[valueLabel].shift(1))
	fiveTickAverage = multiDayAnalysisTools.genXDayAverage(newDF, 5, valueLabel)
	tenTickAverage = multiDayAnalysisTools.genXDayAverage(newDF, 10, valueLabel)
	newDF[series + 'fiveVsTenTickAverage'] = (fiveTickAverage - tenTickAverage).div(tenTickAverage)
	
	ticks = 20
	newDF[series + 'bPercent'] = multiDayAnalysisTools.bBandPercent(newDF, ticks,valueLabel)
	newDF = dateDF.merge(newDF, right_on = 'Date', left_on = 'Date', how = 'left')
	seriesDFList.append(newDF)
os.chdir("data")


quandlRoot = 'quandlData/'
fileNames = ['AAII-AAII_SENTIMENT.csv', 'CASS-CFI.csv', 'CASS-CTLI.csv', 'USMISERY-INDEX.csv', 'WORLDAL-PALPROD.csv']
df = pd.read_csv(quandlRoot + fileNames[0], usecols = ['Date','Bull-Bear Spread', 'Neutral'], parse_dates = ['Date'])
df = dateDF.merge(df, right_on = 'Date', left_on = 'Date', how = 'left')
seriesDFList.append(df)
df = pd.read_csv(quandlRoot + fileNames[1], usecols = ['Date','Shipments Index'], parse_dates = ['Date'])
df = dateDF.merge(df, right_on = 'Date', left_on = 'Date', how = 'left')
seriesDFList.append(df)
df = pd.read_csv(quandlRoot + fileNames[2], usecols = ['Date','Index'], parse_dates = ['Date'])
df.columns = ['Date', 'CASS-CTLI-Index']
df = dateDF.merge(df, right_on = 'Date', left_on = 'Date', how = 'left')
seriesDFList.append(df)
df = pd.read_csv(quandlRoot + fileNames[3], usecols = ['Date','Misery Index'], parse_dates = ['Date'])
df = dateDF.merge(df, right_on = 'Date', left_on = 'Date', how = 'left')
seriesDFList.append(df)
df = pd.read_csv(quandlRoot + fileNames[4], usecols = ['Date','North America', 'China (Estimated)'], parse_dates = ['Date'])
df = dateDF.merge(df, right_on = 'Date', left_on = 'Date', how = 'left')
seriesDFList.append(df)


masterDF = seriesDFList[0].copy()
counter = 0
for df in seriesDFList:
	if counter != 0:
		masterDF= masterDF.merge(df, right_on = 'Date', left_on = 'Date')
	else:
		counter += 1
masterDF.fillna(method = 'ffill', inplace = True)
masterDF.dropna(inplace = True)
masterDF.to_csv('economicIndicators.csv', index = False)