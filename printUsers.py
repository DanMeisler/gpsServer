import os
from pymongo import MongoClient
from consts import *

os.startfile(mongodPath)
mongoClient = MongoClient()
db = mongoClient['gpsDB']
users = db['users']

for x in users.find():
    print(x)
