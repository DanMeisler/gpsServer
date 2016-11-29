from pymongo import MongoClient
from consts import *
import os

os.startfile(mongodPath)
mongoClient = MongoClient()
db = mongoClient['gpsDB']
history = db['history']
currentState = db['currentState']
history.delete_many({})
currentState.delete_many({})
