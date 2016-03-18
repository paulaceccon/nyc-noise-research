/* global complaints_colors, map, layers_311, L, permits_colors, complaints, permits */

// Loads 311 complaints and permits data
function loadData(startDate, endDate)
{
    query311Complaints(startDate, endDate);
    queryPermits(startDate, endDate);
}

function addDataToMap()
{
    loadDataIntoMap('311');
    loadDataIntoMap('Permits');
}

// Formats the date into the appropriated format for the 311 query
function formatDate(date, type)
{
    var d = new Date(date || Date.now()),
            month = '' + (d.getMonth() + 1),
            day = '' + d.getDate(),
            year = d.getFullYear();

    if (month.length < 2)
        month = '0' + month;
    if (day.length < 2)
        day = '0' + day;

    if (type === '311')
        return [year, month, day].join('-');
    if (type === 'Permit')
        return [month, day, year].join('/');
}

// Recovers 311 complaints
function query311Complaints(startDate, endDate)
{
    var start_date = formatDate(startDate, '311') + "T00:00:00";                                 //YYYY-MM-DD
    var end_date = formatDate(endDate, '311') + "T23:59:59";                                 //YYYY-MM-DD
    var complaint_type = 'Noise';                                                                // Complaint Type
    var descriptors = ['Alarms', 'Banging/Pounding', 'Car/Truck Horn', 'Construction Equipment', // Descriptors
        'Construction Before/After Hours', 'Jack Hammering', 'Engine Idling'];

    // Query URL
    var URL = "http://data.cityofnewyork.us/resource/fhrw-4uyv.json";   // API Access Endpoint
    URL += "?";                                                         // A query parameter name is preceded by the question mark
    URL += "$where=";                                                   // Filters to be applied
    URL += "(latitude IS NOT NULL)";                                    // Only return records with coordinates
    URL += " AND ";
    URL += "(complaint_type like '%" + complaint_type + "%')";
    URL += " AND ";
    for (var i = 0; i < descriptors.length - 1; i++)
        URL += "descriptor='" + descriptors[i] + "' OR ";
    URL += "descriptor='" + descriptors[i] + "' AND ";
    URL += "(created_date>='" + start_date + "') AND (created_date<='" + end_date + "')"; // Date range
    URL += "&$group=created_date,descriptor,latitude,longitude";                          // Fields to group by
    URL += "&$select=created_date,descriptor,latitude,longitude";

    URL = encodeURI(URL);

//    console.log(URL);

    $.ajax({async: false, timeout: 30000, url: URL, success: function (data)
        {
            // No data matching the query
            if (data === undefined)
            {
                return;
            }

            // Save the result
            query_result_311 = data;
        }
    });
}

// Recovers permits
function queryPermits(startDate, endDate)
{
    var start_date = formatDate(startDate, 'Permit') + "00:00:00";                               //YYYY-MM-DD
    var end_date = formatDate(endDate, 'Permit') + "23:59:59";                               //YYYY-MM-DD
    var descriptors = ['ALTERATION', 'ALTERATION', 'PLUMBING', 'EQUIPMENT WORK', // Descriptors
        'EQUIPMENT', 'FOUNDATION', 'NEW BUILDING', 'SIGN', 'FULL DEMOLITION'];

    var URL = "https://data.cityofnewyork.us/resource/24as-fxn4.json";  // API Access Endpoint
    URL += "?";                                                         // A query parameter name is preceded by the question mark
    URL += "$where=";                                                   // Filters to be applied
    URL += "(latitude_wgs84 IS NOT NULL)";                                    // Only return records with coordinates
    URL += " AND ";
    for (var i = 0; i < descriptors.length - 1; i++)
        URL += "permit_type_description='" + descriptors[i] + "' OR ";
    URL += "permit_type_description='" + descriptors[i] + "' AND ";
    URL += "(permit_issuance_date>='" + start_date + "') AND (permit_expiration_date<='" + end_date + "')"; // Date range
    URL += "&$group=permit_issuance_date,permit_type_description,latitude_wgs84,longitude_wgs84";                   // Fields to group by
    URL += "&$select=permit_issuance_date,permit_type_description,latitude_wgs84,longitude_wgs84";

    URL = encodeURI(URL);

//    console.log(URL);

    $.ajax({async: false, timeout: 30000, url: URL, success: function (data)
        {
            // No data matching the query
            if (data === undefined)
            {
                return;
            }

            // Save the result
            query_result_permits = data;
        }
    });
}

// Loads 311 complaints into map
function loadDataIntoMap(type)
{
    var colors;
    var data;
    var points = [];
    var count;
    var lat, lon, desc;
    if (type === '311')
    {
        colors = complaints_colors;
        data   = query_result_311;
        lat    = "latitude";
        lon    = "longitude";
        desc   = "descriptor";
        count  = {'Alarms': 0, 'Banging/Pounding': 0, 'Car/Truck Horn': 0, 'Engine Idling': 0,
            'Construction Equipment': 0, 'Construction Before/After Hours': 0, 'Jack Hammering': 0};
        cleanMap(layers_311, layer_311, overlays_311); 
    } else if (type === 'Permits')
    {
        colors = permits_colors;
        data   = query_result_permits;
        lat    = "latitude_wgs84";
        lon    = "longitude_wgs84";
        desc   = "permit_type_description";
        count  = {'ALTERATION': 0, 'PLUMBING': 0, 'EQUIPMENT WORK': 0,
            'EQUIPMENT': 0, 'FOUNDATION': 0, 'NEW BUILDING': 0, 'SIGN': 0,
            'FULL DEMOLITION': 0};
        cleanMap(layers_permits, layer_permits, overlays_permits);
    }

    var overlays = {};
    var markers = {};
    var layers = {};
    for (var key in colors)
        markers[key] = [];

    var all_markers = [];

    $.each(data, function (index, rec)
    {
        if (rec.hasOwnProperty(lat) && rec.hasOwnProperty(lon))
        {
            var marker;
            for (key in colors)
            {
                if (rec[desc].indexOf(key) > -1)
                {
                    points.push([rec[lon], rec[lat], key]);
                    count[key] += 1;

                    marker = L.circleMarker([rec[lat], rec[lon]], marker_style(key, type));
                    markers[key].push(marker);
                    all_markers.push(marker);
                    break;
                }
            }
        }
    });
    
    var all_layers = L.featureGroup(all_markers);
    for (var key in markers)
    {
        layers[key] = L.featureGroup(markers[key]).addTo(map);
        layers[key].bringToFront();
    }
    map.fitBounds(all_layers.getBounds());

    for (var key in colors)
    {
        overlays['<div style="background:' + getColor(key, type) + '; border-radius: 50%; width: 10px; height: 10px; display:inline-block;"></div> ' + key] = layers[key];
    }

    var layer = L.control.layers(null, overlays, {position: 'bottomright'}).addTo(map);

    if (type === '311')
    {
        layers_311 = layers;
        layer_311 = layer;
        overlays_311 = overlays;
        points_311 = pointInPolygon(points, complaints_colors);
    } else if (type === 'Permits')
    {
        layers_permits = layers;
        layer_permits = layer;
        overlays_permits = overlays;
        points_permits = pointInPolygon(points, permits_colors);
    }
}

// Cleans the map current markers and control 
function cleanMap(layers, layer, overlays)
{
    for (var key in layers)
    {
        map.removeLayer(layers[key]);
    }
    if (Object.keys(overlays).length)
        layer.removeFrom(map);
}

// Defines the marker style for each marker
function marker_style(key, type)
{
    return {
        fillColor: getColor(key, type),
        radius: 4,
        weight: 0,
        opacity: 1,
        color: 'white',
        fillOpacity: 0.9
    };
}

// Gets the color of a specific noise descriptor
function getColor(key, type)
{
    if (type === "311")
        return complaints_colors[key];
    else if (type === 'Permits')
        return permits_colors[key];
}