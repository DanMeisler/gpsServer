from consts import *
from pymongo import MongoClient


os.startfile(mongodPath)
mongoClient = MongoClient()
db = mongoClient['gpsDB']
currentState = db['currentState']


def getModems():
    for doc in currentState.aggregate([
        {
            '$group': {
                '_id': {
                    'Modem ID': '$Modem ID',
                    'Date': '$Date',
                    'Latitude': '$Latitude',
                    'Longitude': '$Longitude'
                },
                'units': {
                    '$push': {
                        'Unit ID': '$Unit ID',
                        'MCU_TEMPERATURE': '$MCU_TEMPERATURE'
                    }
                }
            },
        }

    ]):
        try:
            lat = doc['_id']['Latitude']
            lon = doc['_id']['Longitude']
            info = '<h3>Modem ID:{} ({})</h3>'.format(doc['_id']['Modem ID'], doc['_id']['Date'])
            for unit in doc['units']:
                info += '<br>'
                info += '{}: {}\t'.format('Unit ID', unit['Unit ID'])
                info += '{}: {}\t'.format('MCU_TEMPERATURE', unit['MCU_TEMPERATURE'])
            yield (lat, lon, info)
        except TypeError:
            pass


class Map(object):
    def __init__(self):
        self._points = []

    def add_point(self, aPoint):
        self._points.append(aPoint)

    # noinspection PyUnresolvedReferences
    def __str__(self):
        if len(self._points) is 0:
            return ''
        centerLat = sum((x[0] for x in self._points)) / len(self._points)
        centerLon = sum((x[1] for x in self._points)) / len(self._points)
        markersCode = "\n".join(
            ["""
        marker = new google.maps.Marker({{
            position: new google.maps.LatLng({lat}, {lon}),
            map: map
        }});
        google.maps.event.addListener(marker, 'click', function() {{
            infoWindow.close();
            infoWindow = new google.maps.InfoWindow({{
                content: "{info}"
            }});
            infoWindow.open(map, this);
            google.maps.event.addListenerOnce(map, 'mousemove', function() {{
                infoWindow.close();
            }});
        }});""".format(lat=x[0], lon=x[1], info=x[2]) for x in self._points])
        return """
<script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCDScN9rVkda4l9rzwRT-xb-3jdCdnO_bY&v=3.exp&sensor=false"></script>
    <div id="map-canvas" style="height: 100%; width: 100%"></div>
<script type="text/javascript">
    var map, marker;
    var infoWindow = new google.maps.InfoWindow({{
                content: ""
            }});
    function show_map() {{
        map = new google.maps.Map(document.getElementById("map-canvas"), {{
            zoom: 8,
            center: new google.maps.LatLng({centerLat}, {centerLon})
        }});
{markersCode}
}}
    google.maps.event.addDomListener(window, 'load', show_map);
</script>""".format(centerLat=centerLat, centerLon=centerLon,
                    markersCode=markersCode)


if __name__ == "__main__":
    aMap = Map()
    for point in getModems():
        aMap.add_point(point)
    with open(pathMap, "w") as out:
        print(aMap, file=out)
