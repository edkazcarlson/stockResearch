import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.utils import shuffle
import os

splitRatio = .7
testTrainDir = 'sectorTrainTestDir'
go = False
for file in os.listdir('by_sector'):
	sector = file.split('.')[0]
	if sector == 'Technology':
		go = True
	if go:
		print(sector)
		file = 'by_sector/' + file
		chunks = pd.read_csv(file, chunksize = 2000)
		tickerSet = set()
		industrySet = set()
		for chunk in chunks:
			tickerSet = tickerSet.union(chunk['ticker'].unique())
			industrySet = industrySet.union(chunk['industry'].unique())

		chunks = pd.read_csv(file, chunksize = 2000)
		first = True
		for chunk in tqdm(chunks):
			chunk = shuffle(chunk)
			chunkSize = len(chunk)
			splitLine = int(chunkSize * splitRatio)
			rowCount = chunk.shape[0]
			emptyCol = [0] * rowCount
			for ticker in tickerSet:
				chunk['ticker_' + ticker] = chunk['ticker'].apply(lambda x: 1 if x == ticker else 0)
				
			for industry in industrySet:
				chunk['indsutry_' + industry] = chunk['industry'].apply(lambda x: 1 if x == industry else 0)
			chunk.drop(columns = ['industry', 'ticker'], inplace = True)
			if first:
				chunk[0:splitLine].to_csv('{}/{}-{}.csv'.format(testTrainDir, sector, 'train'),index = False)
				chunk[splitLine:].to_csv('{}/{}-{}.csv'.format(testTrainDir, sector, 'test'), index = False)
				first = False
			else:
				chunk[0:splitLine].to_csv('{}/{}-{}.csv'.format(testTrainDir, sector, 'train'), mode = 'a', header = False,index = False)
				chunk[splitLine:].to_csv('{}/{}-{}.csv'.format(testTrainDir, sector, 'test'), mode = 'a', header = False,index = False)
