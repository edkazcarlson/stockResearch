from catboost import CatBoostClassifier, Pool
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

def errorScoreCalculator(predictor, attributes, labels):
	predicted = predictor.predict(attributes)
	errorScore = 0
	for guessIndex in range(len(predicted)):
		guess = predicted[guessIndex]
		actual = labels[guessIndex]
		if guess == 'hold' :
			if actual == 'hold' or actual == 'long':
				errorScore += 1
			else:
				errorScore += 5
		elif guess == 'long':
			if actual == 'short':
				errorScore += 10
			if actual == 'hold':
				errorScore += 5
		else: #short
			if actual == 'long':
				errorScore += 10
			if actual == 'hold':
				errorScore += 5
	print('Error score is : ', errorScore/len(predicted))
	return errorScore
	
combinedDF = pd.read_csv('combinedDF.csv', parse_dates = True)
combinedDF.drop(columns=['tmmrwChngAsPerc', 
		'fiveDayWeightedAverage', 'tenDayWeightedAverage', 'fiveDaySlopeChange', 'tenDaySlopeChange', 
		'ticker', 'High', 'Low', 'Open', 'Close', 'Volume', 'fiveDayAverage', 'tenDayAverage',
		'SEC filings', 'Address of Headquarters', 'Date first added', 'CIK', 'Security'], inplace = True)

sectorList = combinedDF['GICS Sector'].copy().unique()
for sector in sectorList:
	print('Sector is: ', sector)
	sectorDF = combinedDF[combinedDF['GICS Sector'] == sector].copy()
	zScoreAnswer = sectorDF['zScoreOfChangeTmmrw']
	zScoreAnswer = zScoreAnswer.astype('float')
	zScoreAnswer = ['long' if x > .9 else 'short' if x < -.9 else 'hold' for x in zScoreAnswer ]
	fiveDayChangeAnswer = sectorDF['percentChangeInFiveDays']
	fiveDayChangeAnswer = ['long' if x > .05 else 'short' if x < -.05 else 'hold' for x in fiveDayChangeAnswer]
	
	sectorDF.drop(columns = ['zScoreOfChangeTmmrw','percentChangeInFiveDays', 'GICS Sector'], inplace = True)

	masterList = sectorDF.values
	catIndicies = [len(masterList[0]) - 1]
	masterTrainList, masterTestList, zScoreTrainList, zScoreTestList, fiveDayChangeTrainList, fiveDayChangeTestList =\
	train_test_split(masterList,zScoreAnswer,fiveDayChangeAnswer,test_size = .3)

	trainPools = [Pool(data = masterTrainList, label = zScoreTrainList, cat_features = catIndicies),
	Pool(data = masterTrainList, label = fiveDayChangeTrainList, cat_features = catIndicies)]
	testPools = [Pool(data = masterTestList, label = zScoreTestList, cat_features = catIndicies),
	Pool(data = masterTestList, label = fiveDayChangeTestList, cat_features = catIndicies)]
	modelNames = ['ZScorePredictor','FiveDayPredictor']

	for name, train, test in zip(modelNames, trainPools, testPools):
		print(modelNames)
		model = CatBoostClassifier()
		model.fit(train, eval_set = test, logging_level = 'Silent')
		sector = sector.replace(' ', '_')
		model.save_model(name + sector + '.mlmodel')
		print('Score: ', model.score(test))	
		errorScoreCalculator(model, test,test.get_label())
