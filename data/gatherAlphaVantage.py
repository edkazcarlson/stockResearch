import csv
sectorDataPath = 'nyse/securities.csv'
with open(sectorDataPath, newline = '') as csvfile:
	reader = csv.reader(csvfile, delimeter = ',')
	for row in reader:
		ticker = row[0]
		url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol='+ ticker +'&apikey=' + key + '&datatype=csv'
		