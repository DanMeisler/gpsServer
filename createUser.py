import sys
from pymongo import MongoClient
from consts import *
import os

os.startfile(mongodPath)
mongoClient = MongoClient()
db = mongoClient['gpsDB']
users = db['users']

try:
    user = {'username': sys.argv[1], 'password': sys.argv[2], 'isAdmin': sys.argv[3]}
    users.delete_many({'username': sys.argv[1]})
    users.insert_one(user)
    sys.exit(0)
except:
    sys.exit(-1)
