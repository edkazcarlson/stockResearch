import pandas as pd
from textblob import TextBlob
import datetime
import numpy as np
import multiDayAnalysisTools

destFileName = 'sentimentIndicators.csv'
chunks = pd.read_csv('all-the-news-2-1/all-the-news-2-1.csv', usecols = ['date', 'title', 'publication'], 
dtype = {'title':str, 'publication':str}, chunksize = 50000, parse_dates = ['date'])

counter = 0
for chunk in chunks:
	counter += 1
	chunk['sent'] = chunk['title'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
	chunk.drop(columns = ['title', 'publication'], inplace = True)
	chunk['date'] = chunk['date'].dt.strftime('%m/%d/%Y')
	try:
		chunk.to_csv(destFileName, mode = 'a', header = False,index = False)
	except:
		chunk.to_csv(destFileName, index = False)

df = pd.read_csv(destFileName, names = ['Date', 'sent'])
for date in df['Date'].unique():
	daySent = df[df['Date'] == date]['sent']
	dayMean = daySent.mean()
	df = df[df['Date'] != date]
	d = {'Date': [date], 'sent': [dayMean] }
	toAppend = pd.DataFrame(data = d)
	df = df.append(toAppend)
df.sort_values(by =['Date'], inplace = True, ascending = False)
df['changeSinceYesterday'] = (df['sent'] - df['sent'].shift(1))

dateRange = np.arange('2016-01-01', '2020-05-26', dtype='datetime64[D]')
dateRange = {'Date': dateRange}
dateDF = pd.DataFrame(data = dateRange)
df['Date'] = pd.to_datetime(df['Date'])
newDF = dateDF.merge(df, right_on = 'Date', left_on = 'Date', how = 'left')
newDF.fillna(method = 'ffill', inplace = True)
newDF.to_csv(destFileName, index = False)
