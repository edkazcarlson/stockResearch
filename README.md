A personal stock market trading bot to help automate trading stocks.

Strategy:
The general strategy is to predict the Z score of a stocks performance, and then determine whether it is a safe long, short, or if it is too unpredictable to touch.  
The bot also predicts the Z score for the overall performance of the market for the next day.
Using the recommended positions the algorithim chooses, the trading bot then goes long or short on certain stocks.  
The daily breakdown of the "budget" for this is determined by the predicted Z score of the overall market performance, defaulting at a 70-30 split of long vs short positions for an average day.

Using https://alpaca.markets/ as the  stock trading API

Data sets used:
News articles - https://components.one/datasets/all-the-news-2-news-articles-dataset/
Company Data - https://www.kaggle.com/dgawlik/nyse
Stock Data - https://www.kaggle.com/jacksoncrow/stock-market-dataset

Quandl codes used:
AAII/AAII_SENTIMENT - AAII Investor Sentiment Data
USMISERY/INDEX - United States Misery Index
CASS/CFI - Cass Freight Index
CASS/CTLI - Cass Truckload Linehaul Index
WORLDAL/PALPROD - Primary Aluminium Production

Fred codes used:
DTWEXAFEGS - Trade Weighted U.S. Dollar Index: Advanced Foreign Economies, Goods and Services
DPRIME - Bank Prime Loan Rate 
TOTCI - Commercial and Industrial Loans, All Commercial Banks
UNRATE - Unemployment Rate
CONSUMER - Consumer Loans, All Commercial Banks
BUSLOANS - Commercial and Industrial Loans, All Commercial Banks
CCLACBW027SBOG - Consumer Loans: Credit Cards and Other Revolving Plans, All Commercial Banks
STLFSI2 - St. Louis Fed Financial Stress Index
PRS85006092 - Nonfarm Business Sector: Real Output Per Hour of All Persons  
TCU - Capacity Utilization: Total Industry
BOPGSTB - Trade Balance: Goods and Services, Balance of Payments Basis  
CPIAUCSL - Consumer Price Index for All Urban Consumers: All Items in U.S. City Average  
SFTPINDM114SFRBSF - San Francisco Tech Pulse
WALCL - Assets: Total Assets: Total Assets (Less Eliminations from Consolidation): Wednesday Level  
M1 - M1 Money Stock
GOLDAMGBD228NLBM - Gold Fixing Price 10:30 A.M. (London time) in London Bullion Market, based in U.S. Dollars  
PCEC96 - Real Personal Consumption Expenditures  
DGS30 - 30-Year Treasury Constant Maturity Rate  
DGS2 - 2-Year Treasury Constant Maturity Rate
WPU0911 - Producer Price Index by Commodity for Pulp, Paper, and Allied Products: Wood Pulp  
DJIA - Dow Jones Industrial Average
SP500 - S&P 500
DEXCHUS - China / U.S. Foreign Exchange Rate  
DEXUSUK - U.S. / U.K. Foreign Exchange Rate  
NASDAQCOM - NASDAQ Composite Index  
WILL5000PR - Wilshire 5000 Price Index  
NASDAQ100 - NASDAQ 100 Index
DEXSZUS - Switzerland / U.S. Foreign Exchange Rate
DEXJPUS - Japan / U.S. Foreign Exchange Rate