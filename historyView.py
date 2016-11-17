import sys
import os
from datetime import datetime
from consts import *
from pymongo import MongoClient

os.startfile(mongodPath)
mongoClient = MongoClient()
db = mongoClient['gpsDB']
history = db['history']


def createHtml(dateFilter):
    dataRows = "\n".join(["""<tr>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
</tr>""".format(doc[attrNames[0]], doc[attrNames[1]], doc[attrNames[2]],
                doc[attrNames[3]], doc[attrNames[4]], doc[attrNames[5]],
                doc[attrNames[6]], doc[attrNames[7]], doc[attrNames[8]],
                doc[attrNames[9]]) for doc in history.find(dateFilter)])
    return """<?php
    require_once('authenticate.php');
    unlink('history.php');
?>
<table style='border:1px solid red border-collapse:collapse' border='1px'>
    <thead>
    <tr>
        <th>{}</th>
        <th>{}</th>
        <th>{}</th>
        <th>{}</th>
        <th>{}</th>
        <th>{}</th>
        <th>{}</th>
        <th>{}</th>
        <th>{}</th>
        <th>{}</th>
    </tr>
    </thead>
    <tbody>
        {}
    </tbody>
</table>""".format(*attrNames, dataRows)


if __name__ == "__main__":
    try:
        fromDate = datetime.strptime(sys.argv[1], '%Y-%m-%d')
    except:
        fromDate = datetime(1970, 1, 1)
    try:
        toDate = datetime.strptime(sys.argv[2], '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
    except:
        toDate = datetime.now()

    filterOfDates = {attrNames[9]: {'$lte': toDate, '$gte': fromDate}}
    with open(pathHistory, "w") as out:
        print(createHtml(filterOfDates), file=out)
