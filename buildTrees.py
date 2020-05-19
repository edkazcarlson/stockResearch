import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
import os
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
import json
import os

masterDF = pd.read_csv('masterDF.csv', parse_dates = True)
zScoreAnswer = masterDF['zScoreOfChangeTmmrw']
zScoreAnswer = ['long' if x > .1 else 'short' if x < -.7 else 'hold' for x in zScoreAnswer ]
fiveDayChangeAnswer = masterDF['percentChangeInFiveDays']
fiveDayChangeAnswer = ['long' if x > .1 else 'short' if x < -.1 else 'hold' for x in fiveDayChangeAnswer]

masterDF = masterDF.drop(columns=['Date','zScoreOfChangeTmmrw','percentChangeInFiveDays', 'tmmrwChngAsPerc', \
								  'ticker', 'High', 'Low', 'Open', 'Close', 'Volume'])
masterList = masterDF.values
masterTrainList, masterTestList, zScoreTrainList, zScoreTestList, fiveDayChangeTrainList, fiveDayChangeTestList =\
train_test_split(masterList,zScoreAnswer,fiveDayChangeAnswer,test_size = .25)

zScorePredictor = RandomForestClassifier(min_samples_split = 10, n_estimators = 50, random_state = 1, n_jobs = 2)
zScorePredictor.fit(masterTrainList, zScoreTrainList)
fiveDayChangePredictor = RandomForestClassifier(min_samples_split = 10, n_estimators = 50, random_state = 1, n_jobs = 2)
fiveDayChangePredictor.fit(masterTrainList, fiveDayChangeTrainList)
pickle.dump(zScorePredictor, open('zScorePredictor.pkl', "wb"))
pickle.dump(fiveDayChangePredictor, open('fiveDayChangePredictor.pkl', "wb"))
print('dumped')

zScorePredictions = zScorePredictor.predict(masterTestList)
zScorePredictionAccuracy = accuracy_score(zScoreTestList,zScorePredictions)
print('zScorePredictionAccuracy is : ', zScorePredictionAccuracy , '%')
fiveDayPrediction = fiveDayChangePredictor.predict(masterTestList)
fiveDayPredictionAccuracy = accuracy_score(fiveDayChangeTestList,fiveDayPrediction)
print('fiveDayPredictionAccuracy is : ', fiveDayPredictionAccuracy , '%')

zScoreFeature = pd.DataFrame(zScorePredictor.feature_importances_,
									index = masterDF.columns,
									columns=['importance']).sort_values('importance', ascending=False)
print(zScoreFeature.head(10))
fiveDayFeature = pd.DataFrame(fiveDayChangePredictor.feature_importances_,
									index = masterDF.columns,
									columns=['importance']).sort_values('importance', ascending=False)
print(fiveDayFeature.head(10))
zScoreFeature.to_csv('zScoreFeature.csv', index=False) 
fiveDayFeature.to_csv('fiveDayFeature.csv', index=False) 
