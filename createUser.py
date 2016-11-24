import sys
from pymongo import MongoClient
from consts import *
import os

os.startfile(mongodPath)
mongoClient = MongoClient()
db = mongoClient['gpsDB']
users = db['users']

try:
    user = {'username': 'Admin', 'password': '1234', 'isAdmin': True}
    users.delete_many({'username': 'Admin'})
    users.insert_one(user)
    sys.exit(0)
except Exception as e:
    print(e)
    sys.exit(-1)
