import sys
from datetime import datetime
import os
from consts import *
from pymongo import MongoClient

os.startfile(mongodPath)
mongoClient = MongoClient()
db = mongoClient['gpsDB']
currentState = db['currentState']


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
                doc[attrNames[9]]) for doc in currentState.find(dateFilter)])
    return """<?php
    require_once('authenticate.php');
    unlink('currentState.php');
?>
<link rel="stylesheet" type="text/css" href="./DataTables/datatables.css">
<script type="text/javascript" charset="utf8" src="./DataTables/jquery-3.1.1.min.js"></script>
<script type="text/javascript" charset="utf8" src="./DataTables/datatables.js"></script>
<script type="text/javascript" charset="utf8">
    $(document).ready( function () {{
        $('#currentState_table').DataTable();
    }} );
</script>
<table id="currentState_table">
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
    with open(pathCurrentState, "w") as out:
        print(createHtml(filterOfDates), file=out)
