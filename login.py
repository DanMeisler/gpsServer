import os
import sys
from pymongo import MongoClient
from consts import *

os.startfile(mongodPath)
mongoClient = MongoClient()
db = mongoClient['gpsDB']
users = db['users']

try:
    user = users.find_one({'username': sys.argv[1], 'password': sys.argv[2]})
    if user:
        if user['isAdmin']:
            print('Admin')
        else:
            print('User')
    else:
        sys.exit(-1)
except:
    sys.exit(-1)

