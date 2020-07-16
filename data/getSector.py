import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import random
import time
import os
import sys
from fake_useragent import UserAgent

startAt = None
canStart = True
if len(sys.argv) == 2:
	startAt = sys.argv[1]
	canStart = False
print(startAt)
ua = UserAgent()

filePath = '541298_1054465_bundle_archive/stocks' 
fileList = os.listdir(filePath)
baseURL = 'https://finance.yahoo.com/quote/{}/profile?p={}'
dfDestFilePath = 'scrapedSectors.csv'

sectorDF = pd.DataFrame(data = {'ticker': [], 'sector': [], 'industry': []})

for ticker in fileList:
	ticker = ticker.split('.csv')[0].upper()
	if canStart:		
		tickerList = []
		sectorList = []
		industryList = []
		getSector = False
		getIndustry = False
		sector = None
		industry = None
		print(ticker)	
		try:
			response = requests.get(baseURL.format(ticker, ticker),  headers = {'User-Agent': ua.random})
			response.encoding = 'utf-8'
			soup = BeautifulSoup(response.text, features="html.parser")
			for span in soup.find_all('span'):
				if getSector:
					sector = span.contents[0]
					getSector = False
				elif getIndustry:
					industry = span.contents[0]
					getIndustry = False
				else :
					if (len(span.contents) != 0 and span.contents[0] == 'Sector(s)'):
						getSector = True
					elif (len(span.contents) != 0 and span.contents[0] == 'Industry'):
						getIndustry = True
			if (sector != None and industry != None):
				tickerList.append(ticker)
				industryList.append(industry)
				sectorList.append(sector)
				df = pd.DataFrame({'ticker': tickerList, 'sector': sectorList , 'industry': industryList})
				if ticker == 'A':
					df.to_csv(dfDestFilePath, index = False)
				else:
					df.to_csv(dfDestFilePath, mode = 'a', header = False,index = False)
			
		except:
			print('failed to get data for:{}'.format(ticker))
		time.sleep(random.random() * 5 + 5)
	else :
		if ticker == startAt:
			canStart = True

