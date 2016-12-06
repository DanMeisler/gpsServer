from xml.etree import ElementTree as Et
from pymongo import MongoClient
from threading import Thread
from time import sleep

pathOfKml = r'C:\Program Files (x86)\EasyPHP-Devserver-16.1\eds-www\sources\kml\uploads\areas.kml'


def getAreas():
    for placemark in Et.parse(pathOfKml).iter('{http://www.opengis.net/kml/2.2}Placemark'):
        coordinates = []
        for coordinate in placemark.find('{http://www.opengis.net/kml/2.2}Polygon/'
                                         '{http://www.opengis.net/kml/2.2}outerBoundaryIs/'
                                         '{http://www.opengis.net/kml/2.2}LinearRing/'
                                         '{http://www.opengis.net/kml/2.2}coordinates').text.split(',0.0')[:-1]:
            coordinates.append([float(coordinate.split(',')[0]), float(coordinate.split(',')[1])])
        yield coordinates, placemark.find('{http://www.opengis.net/kml/2.2}name').text


def point_inside_polygon(x, y, poly):
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1x == p2x:
                        inside = not inside
                    else:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if x <= xinters:
                            inside = not inside

        p1x, p1y = p2x, p2y
    return inside


def sendEmail(doc):
    pass


def getAreaByLonAndLat(longitude, latitude):
    if not longitude or not latitude:
        return ''
    for coordinates, placeName in getAreas():
            if point_inside_polygon(longitude, latitude, coordinates):
                return placeName
    return ''


def updateAreasOnCollection(collection):
    for doc in collection.find(modifiers={"$snapshot": True}):
        longitude = float(doc['LONGITUDE'])
        latitude = float(doc['LATITUDE'])
        newArea = getAreaByLonAndLat(longitude, latitude)
        if doc['AREA'] != newArea:
            sendEmail(doc)
            # update the area


def updateEveryNSeconds(collection, seconds=60):
    while True:
        updateAreasOnCollection(collection)
        sleep(seconds)


if __name__ == '__main__':
    mongoClient = MongoClient()
    db = mongoClient['gpsDB']
    history = db['history']
    currentState = db['currentState']
    Thread(target=updateEveryNSeconds, args=(history, 10)).start()
    Thread(target=updateEveryNSeconds, args=(currentState, 10)).start()
