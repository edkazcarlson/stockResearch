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
seriesOfInterest = ['DTWEXAFEGS','DPRIME', 'TOTCI', 'UNRATE', 'CONSUMER','BUSLOANS','CCLACBW027SBOG','STLFSI2', 'PRS85006092', 'TCU', 'FPCPITOTLZGUSA', 'BOPGSTB', 'IEABC', 'CPIAUCSL',
'SFTPINDM114SFRBSF']
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
	Std = multiDayAnalysisTools.stdDevLastXDays(newDF, ticks,valueLabel)
	Average = multiDayAnalysisTools.genXDayAverage(newDF, ticks, valueLabel)
	upperBand = ((Std).multiply(2) + Average)
	lowerBand = ((Std).multiply(-2) + Average)
	bPercent = []
	for close, upper, lower in zip (newDF[valueLabel], upperBand, lowerBand):
		print(close, upper, lower)
		if upper - lower == 0:
			bPercent.append(0)
		else:
			bPercent.append((close - lower)/(upper - lower))
	newDF[series + 'bPercent'] = bPercent
	newDF = dateDF.merge(newDF, right_on = 'Date', left_on = 'Date', how = 'left')
	seriesDFList.append(newDF)
masterDF = seriesDFList[0].copy()
counter = 0
for df in seriesDFList:
	if counter != 0:
		masterDF= masterDF.merge(df, right_on = 'Date', left_on = 'Date')
	else:
		counter += 1
masterDF.fillna(method = 'ffill', inplace = True)
masterDF.dropna(inplace = True)
os.chdir("data")
masterDF.to_csv('economicIndicators.csv', index = False)