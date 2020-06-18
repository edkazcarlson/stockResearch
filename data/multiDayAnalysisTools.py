import numpy as np
import pandas as pd
import statistics

def genXDayAverage(df, days, tag, **kwargs):
	legalKwargs = ['modifier']
	modifier = None
	if kwargs is not None:
		for key, value in kwargs.items():
			if key in legalKwargs:
				if key == legalKwargs[0]:
					modifier = value
	toReturn = np.array([0] * df.shape[0])
	toReturn = pd.Series(toReturn, dtype = 'float64')
	for x in range(days):
		shiftedSeries = df[tag].shift(x)
		if modifier is not None:
			shiftedSeries = modifier(shiftedSeries)
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

def bBandPercent(df, ticks, valueLabel):
	Std = stdDevLastXDays(df, ticks,valueLabel)
	Average = genXDayAverage(df, ticks, valueLabel)
	upperBand = ((Std).multiply(2) + Average)
	lowerBand = ((Std).multiply(-2) + Average)
	bPercent = []
	for close, upper, lower in zip (df[valueLabel], upperBand, lowerBand):
		if upper - lower == 0:
			bPercent.append(0)
		else:
			bPercent.append((close - lower)/(upper - lower))
	return bPercent;