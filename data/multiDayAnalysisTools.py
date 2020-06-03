import numpy as np
import pandas as pd
import statistics

def genXDayAverage(df, days, tag):
	toReturn = np.array([0] * df.shape[0])
	toReturn = pd.Series(toReturn, dtype = 'float64')
	for x in range(days):
		shiftedSeries = df[tag].shift(x)
		toReturn = toReturn.add(shiftedSeries)
	return toReturn.div(days)

def stdDevLastXDays(df, days,tag):
	toReturn = []
	pastXDayList = [np.nan] * days
	for _,item in df[tag].items():
		pastXDayList.append(item)
		pastXDayList.pop(0)
		try:
			toReturn.append(statistics.stdev(pastXDayList))
		except:
			toReturn.append(np.nan)
	toReturn = pd.Series(toReturn)
	return toReturn

def bBandFn(closeVal, upperBandVal, lowerBandVal):
	return 'Over' if closeVal > upperBandVal else 'Under' if closeVal < lowerBandVal else 'Within' 
