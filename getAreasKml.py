import sys
err = sys.stderr
sys.stderr = open('nul', 'w')  # to silent lxml error (work on windows only)
from fastkml import KML
sys.stderr = err


def getAreas(pathOfKml):
    # Parse the KML doc
    text = open(pathOfKml, encoding='utf-8').read()
    k = KML()
    k.from_string(text)
    document = list(k.features())[0]
    for folder in document.features():
        for p in folder.features():
            points = '{}'.format(p.geometry).replace(' 0.0', '').replace(', ', ',')[9:-2].split(',')
            poly = []
            for point in points:
                poly.append((float(point.split(' ')[0]), float(point.split(' ')[1])))
            yield (p.name, poly)


if __name__ == '__main__':
    path = r'C:\Program Files (x86)\EasyPHP-Devserver-16.1\eds-www\sources\kml\uploads\areas.kml'
    for area in getAreas(pathOfKml=path):
        print(area)
