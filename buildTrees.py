import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
import os
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import KFold
import json
import os

def errorScoreCalculator(forest, attributes, labels):
	predicted = forest.predict(attributes)
	errorScore = 0
	for guessIndex in range(len(predicted)):
		guess = predicted[guessIndex]
		actual = labels[guessIndex]
		if guess == 'hold' and actual != 'hold':
			errorScore += 1
		elif guess == 'long' and actual == 'short':
			errorScore += 10
		elif guess == 'short' and actual == 'long':
			errorScore += 10
		elif actual == 'hold' and guess != 'hold':
			errorScore += 1
	print('Error score is : ', errorScore)
	return errorScore

masterDF = pd.read_csv('masterDF.csv', parse_dates = True)
masterDF.replace([np.inf, -np.inf], np.nan)
masterDF.dropna(inplace=True)

zScoreAnswer = masterDF['zScoreOfChangeTmmrw']
zScoreAnswer = zScoreAnswer.astype('float')
zScoreAnswer = ['long' if x > .15 else 'short' if x < -.15 else 'hold' for x in zScoreAnswer ]
fiveDayChangeAnswer = masterDF['percentChangeInFiveDays']
fiveDayChangeAnswer = ['long' if x > .05 else 'short' if x < -.05 else 'hold' for x in fiveDayChangeAnswer]

masterDF.drop(columns=['Date','zScoreOfChangeTmmrw','percentChangeInFiveDays', 'tmmrwChngAsPerc', 'fiveDayWeightedAverage', 'tenDayWeightedAverage', 'fiveDaySlopeChange', 
								  'tenDaySlopeChange', 'ticker', 'High', 'Low', 'Open', 'Close', 'Volume', 'fiveDayAverage', 'tenDayAverage'], inplace = True)
for col in masterDF.columns:
	print(col)
masterList = masterDF.values

masterTrainList, masterTestList, zScoreTrainList, zScoreTestList, fiveDayChangeTrainList, fiveDayChangeTestList =\
train_test_split(masterList,zScoreAnswer,fiveDayChangeAnswer,test_size = .3)

hyperParamDict = {'accuracy': 0,
'error_score': np.inf,
'min_samples_split': 0,
'min_impurity_decrease': 0}

min_samples_splitChoices = [10,20,50,100]
min_impurity_decreaseChoices = [0, 0.001, 0.01, 0.05, 0.1, 0.15]
trainTestBundles = [['zScorePredictor', zScoreTrainList, zScoreTestList, hyperParamDict.copy()],
['fiveDayChangePredictor',fiveDayChangeTrainList, fiveDayChangeTestList, hyperParamDict.copy()]]


for minSplit in min_samples_splitChoices:
	for minImpurity in min_impurity_decreaseChoices:
		for bundle in trainTestBundles:
			errorScoreList = []
			for randState in range(5):
				predictor = RandomForestClassifier(min_samples_split = minSplit, min_impurity_decrease = minImpurity,
					random_state = randState, n_jobs = 2)
				predictor.fit(masterTrainList, bundle[1])
				predictions = predictor.predict(masterTestList)
				predictionAccuracy = accuracy_score(bundle[2],predictions)
				print(bundle[0] + ' accuracy is : ', predictionAccuracy , '%')
				feature = pd.DataFrame(predictor.feature_importances_,
													index = masterDF.columns,
													columns=['importance']).sort_values('importance', ascending=False)
				print(feature.head(10))
				errorScore = errorScoreCalculator(predictor, masterTestList, zScoreTestList)
				errorScoreList.append(errorScore)
			errorScore = sum(errorScoreList)/len(errorScoreList)
			if errorScore < bundle[3]['error_score']:
				bundle[3]['accuracy'] = predictionAccuracy
				bundle[3]['error_score'] = errorScore
				bundle[3]['min_samples_split']
				bundle[3]['min_impurity_decrease']
print(trainTestBundles)
print(trainTestBundles[0][3])
print(trainTestBundles[1][3])
for bundle in trainTestBundles:
	predictor = RandomForestClassifier(min_samples_split = bundle[3]['min_samples_split'], 
	min_impurity_decrease = bundle[3]['min_impurity_decrease'], random_state = 1, n_jobs = 2)
	predictor.fit(masterTrainList, bundle[1])
	pickle.dump(predictor, open(bundle[0] + '.pkl', 'wb'))