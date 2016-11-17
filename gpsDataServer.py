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


def getRowFromData(aData, time):
    try:
        attrValues = re.split("MID|UID|\$|VB|TPM|TPS", aData)[1:]
        placeName = ''
        gps_data = attrValues[2].split(',')
        lat = latLonParse(gps_data[2][:2], gps_data[2][2:], gps_data[3])
        lon = latLonParse(gps_data[4][:3], gps_data[4][3:], gps_data[5])
        if (not lat) or (not lon):
            return None
        for name, area in getAreas(pathAreas):
            if polygon.point_inside_polygon(lat, lon, area):
                placeName = name
                break
        row = {attrNames[0]: attrValues[0],
               attrNames[1]: attrValues[1],
               attrNames[2]: attrValues[2],
               attrNames[3]: attrValues[3],
               attrNames[4]: attrValues[4],
               attrNames[5]: attrValues[5],
               attrNames[6]: lat,
               attrNames[7]: lon,
               attrNames[8]: placeName,
               attrNames[9]: time}
        return row
    except:
        return None


def clientHandler(conn, client_address):
    print('Connection from {}:{} '.format(*client_address))
    allData = ''
    while True:
        try:
            data = conn.recv(1024).decode('utf-8')
        except ConnectionResetError:
            break
        allData += data
        if not data:
            break
    conn.close()
    time = datetime.now()
    for line in allData.splitlines():
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
