import os
from consts import *
from pymongo import MongoClient


def textPhp():
    os.startfile(mongodPath)
    mongoClient = MongoClient()
    db = mongoClient['gpsDB']
    history = db['history']
    try:
        renderModem = "\n".join(["""
if(data=="{}"){{
    return "{}";
}}
    """.format(*line.strip().split(',')) for line in open(pathRenderModemCsv)])
    except FileNotFoundError:
        renderModem = ''

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
                doc[attrNames[9]]) for doc in history.find()])
    return """<?php
    require_once('authenticate.php');
?>
<link rel="stylesheet" type="text/css" href="//cdn.datatables.net/1.10.12/css/jquery.dataTables.min.css">
<link rel="stylesheet" type="text/css" href="//cdn.datatables.net/buttons/1.2.2/css/buttons.dataTables.min.css">
<script type="text/javascript" charset="utf8" src="//code.jquery.com/jquery-1.12.3.js"></script>
<script type="text/javascript" charset="utf8" src="//cdn.datatables.net/1.10.12/js/jquery.dataTables.min.js"></script>
<script type="text/javascript" charset="utf8" src="//cdn.datatables.net/buttons/1.2.2/js/dataTables.buttons.min.js"></script>
<script type="text/javascript" charset="utf8" src="//cdn.datatables.net/buttons/1.2.2/js/buttons.flash.min.js"></script>
<script type="text/javascript" charset="utf8" src="//cdnjs.cloudflare.com/ajax/libs/jszip/2.5.0/jszip.min.js"></script>
<script type="text/javascript" charset="utf8" src="//cdn.rawgit.com/bpampuch/pdfmake/0.1.18/build/pdfmake.min.js"></script>
<script type="text/javascript" charset="utf8" src="//cdn.rawgit.com/bpampuch/pdfmake/0.1.18/build/vfs_fonts.js"></script>
<script type="text/javascript" charset="utf8" src="//cdn.datatables.net/buttons/1.2.2/js/buttons.html5.min.js"></script>
<script type="text/javascript" charset="utf8" src="//cdn.datatables.net/buttons/1.2.2/js/buttons.print.min.js"></script>
<script type="text/javascript" charset="utf8">
    /* Custom filtering function which will search data in column four between two values */
    $.fn.dataTable.ext.search.push(
        function( settings, data, dataIndex ) {{
            var min = Date.parse( $('#min').val());
            var max = Date.parse( $('#max').val());
            var date = Date.parse( data[9] ) || 0; // use data for the date column

            if ( ( isNaN( min ) && isNaN( max ) ) ||
                 ( isNaN( min ) && date <= max ) ||
                 ( min <= date   && isNaN( max ) ) ||
                 ( min <= date   && date <= max ) )
            {{
                return true;
            }}
            return false;
        }}
    );
    $(document).ready( function () {{
        // Detect page change / auto refresh
        var currenthtml;
        var latesthtml;

        $.get(window.location.href, function(data) {{
            currenthtml = data;
            latesthtml = data;
        }});

        setInterval(function() {{
            $.get(window.location.href, function(data) {{
                latesthtml = data;
            }});

            if(currenthtml != latesthtml) {{
                location.reload();
            }}
        }}, 5000);
        var table = $('#history_table').DataTable({{
            dom: 'Bfrtip',
            buttons: [
                'copy', 'csv', 'excel',
                {{
                    extend: 'pdfHtml5',
                    orientation: 'landscape',
                    pageSize: 'LEGAL'
                }}, 'print'
            ],
            stateSave: true,
            "scrollY": 200,
            "scrollX": true,
            "columnDefs": [
            {{
                "render": function ( data, type, row ) {{
                    {renderModem}
                    return data;
                }},
                "targets": 0
            }}]
        }});
        // Event listener to the two range filtering inputs to redraw on input
        $('#min, #max').keyup( function() {{
            table.draw();
        }} );
    }} );
</script>
<table border="0" cellspacing="5" cellpadding="5">
    <tbody>
        <tr>
            <td>
                <input type="text" id="min" name="min" placeholder="Minimum date:">
            </td>
        </tr>
        <tr>
            <td>
                <input type="text" id="max" name="max" placeholder="Maximum date:">
            </td>
        </tr>
    </tbody>
</table>
<table id="history_table" class="display" cellspacing="0" width="100%">
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
        {dataRows}
    <div style="position: fixed; width: 229px; height: 151px; bottom: 10;left: 10; background-image: url('sources/images/logo.png');">
    </div>
    </tbody>
</table>""".format(*attrNames, renderModem=renderModem, dataRows=dataRows)


def createPhp():
    with open(pathHistory, "w") as out:
        print(textPhp(), file=out)


if __name__ == "__main__":
    createPhp()
