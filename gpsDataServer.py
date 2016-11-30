import os
from getAreasKml import getAreas
import re
import socket
from datetime import datetime
from threading import Thread
import polygon
from consts import *
from pymongo import MongoClient, errors


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 0))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def latLonParse(degrees, minutes, direction):
    try:
        dd = float(degrees) + float(minutes) / 60
        if direction.upper() == 'W' or direction.upper() == 'S':
            dd *= -1
        dd = round(dd, 6)
        return dd
    except:
        return None


def getRowsFromData(aData):
    try:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        unitAttrValues = re.split('UID|UBAT|MVOLIND|UCSQ|NETCON|MCUTMP|EXTTMP|LOC|SPEED|TAGS', aData)[1:]
        loc = unitAttrValues[7]
        gpsData = loc.split(',')
        lat = latLonParse(gpsData[2][:2], gpsData[2][2:], gpsData[3])
        lon = latLonParse(gpsData[4][:3], gpsData[4][3:], gpsData[5])
        placeName = ''
        if lat and lon:
            for name, area in getAreas(pathAreas):
                if polygon.point_inside_polygon(lon, lat, area):  # areas as list of (lon, lat) pairs
                    placeName = name
                    break
        tags = unitAttrValues[9].split(',')
        for tag in tags:
            tagAttrValues = re.split('TID|TBAT|TTMP', tag)[1:]
            row = {
                'DATE': date,
                'UID': unitAttrValues[0],
                'TID': tagAttrValues[0],
                'TTMP': tagAttrValues[0],
                'TBAT': tagAttrValues[1],
                'UBAT': unitAttrValues[1],
                'MVOLIND': unitAttrValues[2],
                'UCSQ': unitAttrValues[3],
                'NETCON': unitAttrValues[4],
                'MCUTMP': unitAttrValues[5],
                'EXTTMP': unitAttrValues[6],
                'AREA': placeName,
                'LOC': loc,
                'LATITUDE': str(lat),
                'LONGITUDE': str(lon),
                'SPEED': unitAttrValues[8]
            }
            yield row
    except Exception as e:
        # print(e)
        return None


def clientHandler(conn, client_address):
    conn.settimeout(30)  # timeout in 30 seconds
    print('Connection from {}:{} '.format(*client_address))
    allData = ''
    while True:
        try:
            data = conn.recv(1024).decode('utf-8')
            if data:
                allData += data
            else:
                break
        except:
            break
    conn.close()
    print('{}:{} sent ({} chars) : "{}"'.format(*client_address, len(allData), allData))
    for row in getRowsFromData(allData):
        if row:
            try:
                history.insert_one(row)
                currentState.delete_many({'TID': row['TID']})
                currentState.insert_one(row)
            except errors.ServerSelectionTimeoutError:
                print('mongodb disconnected...')
                os.startfile(mongodPath)
                print('mongodb connected again')
    print('disconnecting from {}:{} '.format(*client_address))


os.startfile(mongodPath)
mongoClient = MongoClient()
db = mongoClient['gpsDB']
history = db['history']
currentState = db['currentState']
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP/IP socket
server_address = (get_ip(), 10000)  # Bind the socket to the port
print('starting up on {}:{}, mongodb on {}'.format(*server_address, mongoClient.address[1]))
sock.bind(server_address)
sock.listen()  # Listen for incoming connections
while True:
    Thread(target=clientHandler, args=sock.accept()).start()
