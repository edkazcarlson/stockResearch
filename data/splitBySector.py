import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.utils import shuffle

smallPath = 'filtered.csv'
chunks = pd.read_csv(smallPath, chunksize = 2000)
endFilePath = 'by sector/{}.csv'
counter = 0
seenSectors = []
for chunk in tqdm(chunks):
	counter += 1
	chunk = shuffle(chunk)
	rowCount = chunk.shape[0]
	for sector in chunk['sector'].copy().unique():
		sectorDF = chunk[chunk['sector'] == sector]
		if sector in seenSectors:
			sectorDF.to_csv(endFilePath.format(sector), mode = 'a', header = False,index = False)
		else:
			sectorDF.to_csv(endFilePath.format(sector), index = False)
			seenSectors.append(sector)