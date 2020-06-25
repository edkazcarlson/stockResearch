import pandas as pd
from textblob import TextBlob
import datetime
import numpy as np
import multiDayAnalysisTools
from sklearn.model_selection import train_test_split
from textblob.classifiers import NaiveBayesClassifier
import pickle

sectionsToIgnore = ['Games', 'Sex', 'Animation', 'Tonic', 'Art Festivals', 'Oscars', 'US MLB', 'LGBT', 'alcohol', 'Target LGBT', 'wuvable oaf', ' Munchies', 'LGBQT', 'gif six pack', \
'horoscopes', 'Arts', 'Jersey Shore', 'lego-art', 'Art Panel', 'same sex marriage news', 'neo-nazis', 'DIVORCE', 'Rihanna', 'feminism', 'feminist art', '.gif art', '']

def numericalToRange(zScore):
	if zScore < -.85:
		return 'lowest'
	elif zScore < -.255:
		return 'low'
	elif zScore < .255:
		return 'normal'
	elif zScore < .85:
		return 'high'
	else:
		return 'highest'

destFileName = 'customSentimentIndicators.csv'
chunks = pd.read_csv('all-the-news-2-1/all-the-news-2-1.csv', usecols = ['date', 'title', 'article', 'section'], 
dtype = {'title':str, 'article':str}, chunksize = 500, parse_dates = ['date'])
dayPerformance = pd.read_csv('stockDataIndicators.csv', usecols = ['Date', 'thisDayZScore'], parse_dates = ['Date'], dtype = {'thisDayZScore': float})
dayPerformance.drop_duplicates(inplace = True)
dayPerformance['zRange'] = dayPerformance['thisDayZScore'].apply(numericalToRange)
articleTestMaster = None
titleTestMaster = None
zScoreTestMaster = None
titleClassifier = None
articleClassifier = None
counter = 0
for chunk in chunks:
	for section in sectionsToIgnore:
		chunk = chunk[chunk['section'] != section]
	print(chunk['section'].unique())
	counter += 1
	chunk.sort_values(by = ['date'], inplace = True)
	startDate = chunk.iloc[0]['date']
	endDate = chunk.iloc[chunk.shape[0] - 1]['date']
	dateRange = np.arange(startDate, endDate, dtype='datetime64[D]')
	dateRange = {'Date': dateRange}
	dateDF = pd.DataFrame(data = dateRange)
	chunk = dateDF.merge(chunk, right_on = 'date', left_on = 'Date', how = 'left')
	#move the news articles 1 down so they line up with the next days performance
	chunk['article'] = chunk['article'].shift(1)
	chunk['title'] = chunk['title'].shift(1)

	
	#join on date with dayPerformance
	chunk = dayPerformance.merge(chunk, right_on = 'date', left_on = 'Date', how = 'left')
	chunk.dropna(inplace = True)
	#make 3 numpy arrays, article, title, zScoreRange
	numpyOfArticle = chunk['article'].to_numpy()
	numpyOfTitle = chunk['title'].to_numpy()
	numpyOfZScore = chunk['zRange'].to_numpy()

	articleTrain, articleTest, titleTrain,titleTest, zScoreTrain, zScoreTest = train_test_split(numpyOfArticle, numpyOfTitle, numpyOfZScore, test_size = .25)
	if articleTestMaster is None:
		articleTestMaster = articleTest
		titleTestMaster = titleTest
		zScoreTestMaster = zScoreTest
		titleClassifier = NaiveBayesClassifier([(title, score) for title, score in zip(titleTrain, zScoreTrain)])
		articleClassifier = NaiveBayesClassifier([(article, score) for article, score in zip(articleTrain, zScoreTrain)])
	else :
		articleTestMaster = np.append(articleTestMaster, articleTest)
		titleTestMaster =  np.append(titleTestMaster, titleTest)
		zScoreTestMaster =  np.append(zScoreTestMaster, zScoreTest)
		titleClassifier.update(([(title, score) for title, score in zip(titleTrain, zScoreTrain)]))
		articleClassifier.update(([(article, score) for article, score in zip(articleTrain, zScoreTrain)]))
print(titleClassifier.accuracy([(title, zScore) for title, zScore in zip(titleTestMaster, zScoreTestMaster)]))
print(articleClassifier.accuracy([(article, zScore) for article, zScore in zip(articleTestMaster, zScoreTestMaster)]))
pickle.dump(titleClassifier, open('titleClassifier.pkl', 'wb'))
pickle.dump(articleClassifier, open('articleClassifier.pkl', 'wb'))