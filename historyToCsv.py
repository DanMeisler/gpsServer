import csv
import sys
from datetime import datetime
from consts import *
from pymongo import MongoClient

os.startfile(mongodPath)
mongoClient = MongoClient()
db = mongoClient['gpsDB']
history = db['history']

try:
    fromDate = datetime.strptime(sys.argv[1], '%Y-%m-%d')
except:
    fromDate = datetime(1970, 1, 1)
try:
    toDate = datetime.strptime(sys.argv[2], '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
except:
    toDate = datetime.now()

filterOfDates = {attrNames[9]: {'$lte': toDate, '$gte': fromDate}}
with open(pathHistoryCsv, 'w', newline='') as historyFile:
    writer = csv.DictWriter(historyFile, fieldnames=attrNames)
    writer.writeheader()
    for doc in history.find(filterOfDates):
        doc.pop('_id')
        writer.writerow(doc)
