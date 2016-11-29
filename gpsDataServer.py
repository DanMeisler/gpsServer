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
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    unitAttrValues = re.split('UID|UBAT|MVOL|CSQ|NETCON|MCUTMP|EXTTMP|LOC|SPEED|TAGS', aData)[1:]
    loc = unitAttrValues[7]
    gpsData = loc.split(',')
    lat = latLonParse(gpsData[2][:2], gpsData[2][2:], gpsData[3])
    lon = latLonParse(gpsData[4][:3], gpsData[4][3:], gpsData[5])
    tags = unitAttrValues[9].split(',')
    for tag in tags:
        tagAttrValues = re.split('TID|VID', tag)[1:]
        row = {
            'DATE': date,
            'UID': unitAttrValues[0],
            'UBAT': unitAttrValues[1],
            'MVOL': unitAttrValues[2],
            'CSQ': unitAttrValues[3],
            'NETCON': unitAttrValues[4],
            'MCUTMP': unitAttrValues[5],
            'EXTTMP': unitAttrValues[6],
            'LOC': loc,
            'LATITUDE': str(lat),
            'LONGITUDE': str(lon),
            'SPEED': unitAttrValues[8],
            'TID': tagAttrValues[0],
            'VID': tagAttrValues[1]
        }
        yield row


def getRowFromData(aData, time):
    try:
        attrValues = re.split('MID|UID|\$|VB|TPM|TPS', aData)[1:]
        placeName = ''
        gps_data = attrValues[2].split(',')
        lat = latLonParse(gps_data[2][:2], gps_data[2][2:], gps_data[3])
        lon = latLonParse(gps_data[4][:3], gps_data[4][3:], gps_data[5])
        satellitesCount = int(gps_data[7])
        if (not lat) or (not lon) or (satellitesCount < 4):
            pass  # return None TODO
        else:
            for name, area in getAreas(pathAreas):
                if polygon.point_inside_polygon(lon, lat, area):  # areas as list of (lon, lat) pairs
                    placeName = name
                    break
        row = {attrNames[0]: attrValues[0],
               attrNames[1]: attrValues[1],
               attrNames[2]: '$' + attrValues[2],
               attrNames[3]: attrValues[3][:1] + '.' + attrValues[3][1:],
               attrNames[4]: attrValues[4],
               attrNames[5]: attrValues[5],
               attrNames[6]: str(lat),
               attrNames[7]: str(lon),
               attrNames[8]: placeName,
               attrNames[9]: time}
        return row
    except:
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
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for line in allData.split(';'):
        print('{}:{} sent ({} chars) : "{}"'.format(*client_address, len(line), line))
        rowOfData = getRowFromData(line, time)
        if rowOfData:
            try:
                history.insert_one(rowOfData)
                currentState.delete_many({attrNames[1]: rowOfData[attrNames[1]]})
                currentState.insert_one(rowOfData)
            except errors.ServerSelectionTimeoutError:
                print('mongodb disconnected...')
                os.startfile(mongodPath)
                print('mongodb connected again')
    # new implementation using getRowsFromData function
    # for row in getRowsFromData(allData):
    #     if row#:
    #         try:
    #             history.insert_one(rowOfData)
    #             currentState.delete_many({attrNames[1]: rowOfData[attrNames[1]]})
    #             currentState.insert_one(rowOfData)
    #         except errors.ServerSelectionTimeoutError:
    #             print('mongodb disconnected...')
    #             os.startfile(mongodPath)
    #             print('mongodb connected again')
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
