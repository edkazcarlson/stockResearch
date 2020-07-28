import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.utils import shuffle



smallPath = 'filtered.csv'
splitBase = 'smallFiltered-{}.csv'
chunks = pd.read_csv(smallPath, chunksize = 1000)
counter = 0
for chunk in tqdm(chunks):
	counter += 1
	chunk = shuffle(chunk)
	rowCount = chunk.shape[0]
	for x in range(10):
		subDF = chunk[int(x*rowCount * .1):int((1+x)*rowCount * .1)]
		if counter == 1:
			subDF.to_csv(splitBase.format(x), index = False)
		else :
			subDF.to_csv(splitBase.format(x), mode = 'a', header = False,index = False)

