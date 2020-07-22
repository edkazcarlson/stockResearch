import sqlite3
import pandas as pd
#https://stackoverflow.com/questions/305378/list-of-tables-db-schema-dump-etc-using-the-python-sqlite3-api/33100538#33100538
dbPath = 'all-the-news.db'
allTheNewsDumpPath  = 'allTheNewsDump/'
db = sqlite3.connect(dbPath)
cursor = db.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(tables)
for table_name in tables:
	print(table_name)
	table_name = table_name[0]
	table = pd.read_sql_query("SELECT * from %s" % table_name, db)
	print(table.head())
	table.to_csv('{}{}.csv'.format(allTheNewsDumpPath, table_name), index_label='index')
cursor.close()
db.close() 