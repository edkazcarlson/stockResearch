import pandas as pd
from textblob import TextBlob
import datetime
import numpy as np
import multiDayAnalysisTools

destFileName = 'sentimentIndicators.csv'
chunks = pd.read_csv('all-the-news-2-1/all-the-news-2-1.csv', usecols = ['date', 'title', 'article'], 
dtype = {'title':str, 'article':str}, chunksize = 50000, parse_dates = ['date'])

counter = 0
for chunk in chunks:
	counter += 1
	chunk['titleSent'] = chunk['title'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
	chunk['articleSent'] = chunk['article'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
	chunk.drop(columns = ['title', 'article'], inplace = True)
	chunk['date'] = chunk['date'].dt.strftime('%m/%d/%Y')
	try:
		chunk.to_csv(destFileName, mode = 'a', header = False,index = False)
	except:
		chunk.to_csv(destFileName, index = False)

df = pd.read_csv(destFileName, names = ['Date', 'titleSent', 'articleSent'], dtype = {'titleSent': 'float64', 'articleSent': 'float64'}, parse_dates = ['Date'])
for date in df['Date'].unique():
	dayTitleSent = df[df['Date'] == date]['titleSent']
	dayTitleMean = dayTitleSent.mean()
	dayArticleSent = df[df['Date'] == date]['articleSent']
	dayArticleMean = dayArticleSent.mean()
	df = df[df['Date'] != date]
	d = {'Date': [date], 'titleSent': [dayTitleMean], 'articleSent': [dayArticleMean] }
	toAppend = pd.DataFrame(data = d)
	df = df.append(toAppend)
df.sort_values(by =['Date'], inplace = True, ascending = True)
df['titleSentChangeSinceYesterday'] = (df['titleSent'] - df['titleSent'].shift(1))
df['articleSentChangeSinceYesterday'] = (df['articleSent'] - df['articleSent'].shift(1))
df.to_csv(destFileName, index = False)

df = pd.read_csv(destFileName, dtype = {'titleSent': 'float64', 'titleSentChangeSinceYesterday': 'float64', 
'articleSent': 'float64', 'articleSentChangeSinceYesterday': 'float64'}, parse_dates = ['Date'])
days = 25
for x in ['titleSent', 'articleSent']:
	Std = multiDayAnalysisTools.stdDevLastXDays(df, days, x)
	Average = multiDayAnalysisTools.genXDayAverage(df, days, x)
	upperBand = ((Std).multiply(2) + Average)
	lowerBand = ((Std).multiply(-2) + Average)
	bPercent = []
	for close, upper, lower in zip (df[x], upperBand, lowerBand):
		if upper - lower != 0:
			bPercent.append((close - lower)/(upper - lower))
		else:
			bPercent.append(10)
	df[x + 'bPercent'] = bPercent	

dateRange = np.arange('2016-01-01', '2020-05-26', dtype='datetime64[D]')
dateRange = {'Date': dateRange}
dateDF = pd.DataFrame(data = dateRange)
df['Date'] = pd.to_datetime(df['Date'])
newDF = dateDF.merge(df, right_on = 'Date', left_on = 'Date', how = 'left')
newDF.fillna(method = 'ffill', inplace = True)
newDF.to_csv(destFileName, index = False)
