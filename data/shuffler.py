import pandas as pd
import numpy as np
from sklearn.utils import shuffle

smallPath = 'filtered.csv'
splitBase = 'smallFiltered-{}.csv'
df = pd.read_csv(smallPath)
df = shuffle(df)
rowCount = df.shape[0]
for x in range(5):
	print(x*rowCount * .2)
	print((1+x)*rowCount * .2)
	subDF = df[int(x*rowCount * .2):int((1+x)*rowCount * .2)]
	subDF.to_csv(splitBase.format(x), index = False)