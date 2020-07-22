import pandas as pd
from textblob import TextBlob
import datetime
import numpy as np
import multiDayAnalysisTools
pd.set_option('display.max_columns', None)

def dateCleaner(x):
	if len(x) > 10 and x[10] == '"':
		return x[0:10]
	else :
		return x

destFileName = 'sentimentIndicators.csv'

dumpDF = pd.read_csv('allTheNewsDump/longform.csv', usecols = ['date', 'title', 'content'], parse_dates = ['date'])
dumpDF = dumpDF.dropna(subset = ['date'])

print(dumpDF[dumpDF['date'].str.len() > 10])
dumpDF['date'] = dumpDF['date'].apply(lambda x: dateCleaner(x))
dumpDF['date'] = pd.to_datetime(dumpDF['date'])
dumpDF['date'] = dumpDF['date'].dt.strftime('%y/%m/%d')
dumpDF['titleSent'] = dumpDF['title'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
dumpDF['articleSent'] = dumpDF['content'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
dumpDF.drop(columns = ['title', 'content'], inplace = True)
dumpDF.to_csv(destFileName, index = False)

nyTimes = pd.read_csv('nytimes front page.csv', usecols = ['date', 'title', 'stems'], parse_dates = ['date'])
nyTimes['titleSent'] = nyTimes['title'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
nyTimes['articleSent'] = nyTimes['stems'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
nyTimes.drop(columns = ['title', 'stems'], inplace = True)
nyTimes['date'] = nyTimes['date'].dt.strftime('%m/%d/%Y')
nyTimes.to_csv(destFileName, mode = 'a', header = False,index = False)

chunks = pd.read_csv('all-the-news-2-1/filteredNews.csv', usecols = ['date', 'title', 'article', 'section'], 
dtype = {'title':str, 'article':str, 'section':str}, chunksize = 50000, parse_dates = ['date'])

counter = 0
for chunk in chunks:
	counter += 1
	print(chunk['section'].unique())
	chunk['titleSent'] = chunk['title'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
	chunk['articleSent'] = chunk['article'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
	chunk.drop(columns = ['title', 'article'], inplace = True)
	chunk['date'] = chunk['date'].dt.strftime('%m/%d/%Y')
	chunk.to_csv(destFileName, mode = 'a', header = False,index = False)

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

dateRange = np.arange('2013-01-01', '2020-05-26', dtype='datetime64[D]')
dateRange = {'Date': dateRange}
dateDF = pd.DataFrame(data = dateRange)
df['Date'] = pd.to_datetime(df['Date'])
newDF = dateDF.merge(df, right_on = 'Date', left_on = 'Date', how = 'left')
newDF.fillna(method = 'ffill', inplace = True)
newDF.to_csv(destFileName, index = False)
