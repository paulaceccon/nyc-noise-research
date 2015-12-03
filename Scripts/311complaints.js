/* 311 Data */

//---- Map layers
// To store all markers layers
var layers = [];
// To store the control layer
var layer;
// To store all markers per descriptions
var overlays = {}; 

// Data URL variable
var URL;

// Query result
var query_result = "";
									  						  			
//---- Noise variables

// Noise Descriptions	
var noise_description = ['Air Condition/Ventilation Equipment', 
						 'Alarms',
						 'Banging/Pounding', 
						 'Barking Dog', 
						 'Car/Truck Horn', 
						 'Car/Truck Music', 
						 'Construction Equipment', 
						 'Construction Before/After Hours', 
						 'Engine Idling', 
						 'Ice Cream Truck', 
						 'Jack Hammering', 
						 'Lawn Care Equipment',
						 'Loud Music/Party',
						 'Loud Talking',
						 'Loud Television',
						 'Manufacturing Noise',
						 'Private Carting Noise',
						 'Others'];
			
// Noise Description's colors			 
var marker_colors = ['#7f3b08',
					 '#a50026',
					 '#d73027',
					 '#f46d43',
					 '#fdae61',
					 '#fee090',
					 '#ffffbf',
					 '#ffffff',
					 '#e0f3f8',
					 '#abd9e9',
					 '#74add1',
					 '#4575b4',
					 '#313695',
					 '#d8daeb',
					 '#b2abd2',
					 '#8073ac',
					 '#542788',
					 '#000000'];


//---- 311 Query Request

// Builds the query URL based on a date range
// BUGFIX: URL encoding 
function buildQuery(startDate, endDate)
{
	/*http://data.cityofnewyork.us/resource/erm2-nwe9.json?$where=(latitude%20IS%20NOT%20NULL)%
	20AND%20(complaint_type%20like%20%27\%Noise\%%27)%20AND%20(created_date%3E=%272013-08-01%27)%
	20AND%20(created_date%3C=%272013-08-08%27)&$group=complaint_type,descriptor,latitude,longitude&$
	select=descriptor,latitude,longitude,complaint_type*/
	
	var start_date = formattedDate(startDate)+"T00:00:00";  //YYYY-MM-DD
	var end_date = formattedDate(endDate)+"T23:59:59";      //YYYY-MM-DD
	var c_type = 'Noise'; 		   							       // Complaint Type

	// Build the data URL
    URL = "http://data.cityofnewyork.us/resource/fhrw-4uyv.json"; // API Access Endpoint
    URL += "?";                                                   // A query parameter name is preceded by the question mark
    URL += "$where=";                                             // Filters to be applied
    URL += "(latitude IS NOT NULL)";                              // Only return records with coordinates
    URL += " AND ";
    URL += "(complaint_type like '%" + c_type + "%')";
    URL += " AND ";
    URL += "(created_date>='" + start_date + "') AND (created_date<='" + end_date + "')"; // Date range
    URL += "&$group=created_date,descriptor,latitude,longitude";                          // Fields to group by
    URL += "&$select=created_date,descriptor,latitude,longitude";                         // Fields to return

    URL = encodeURI(URL); 
}

// Formats the date into the appropriated input for the query
function formattedDate(date) 
{
    var d = new Date(date || Date.now()),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2) month = '0' + month;
    if (day.length < 2) day = '0' + day;

    return [year, month, day].join('-');
}
	
	
//---- Query results
function getQueryResult()
{
	return query_result;
}

	
//---- Complaints localization

//	Load GeoJSON from an external file
function load311ComplaintsIntoMap(map)
{
	cleanMap();
	$.ajax({async: false, url: URL, success: function(data)
	{
		if ( data.length == 0 ) 
		{
			return;
		}
		
		// Save the result
		query_result = data;
		console.log(query_result);
		
		var markers = []
		for (var i = 0; i < noise_description.length; i++) 
		{
			markers[i] = [];
		}

		var all_markers = [];
		
		$.each(data, function(index, rec)
		{
			if ( rec.hasOwnProperty("latitude") && rec.hasOwnProperty("longitude") )
			{
				var marker;
				for (var i = 0; i < noise_description.length; i++) 
				{
					if (rec.descriptor.indexOf(noise_description[i]) > -1) 
					{
						marker = L.circleMarker([rec.latitude, rec.longitude], marker_style(i));
						markers[i].push(marker); 
						all_markers.push(marker); 
						break;
					}
					if (i == noise_description.length-1) 
					{
						marker = L.circleMarker([rec.latitude, rec.longitude], marker_style(i));
						markers[i].push(marker); 
						all_markers.push(marker); 
					}
				}
			}

		});
	
		// Create layer of all markers but do not add to map
		var all_layers = L.featureGroup(all_markers);		
		// Create specific layers of markers and add to map
		for (var i = 0; i < markers.length; i++) 
		{
			layers[i] = L.featureGroup(markers[i]).addTo(map);
			layers[i].bringToFront();
		}
		map.fitBounds(all_layers.getBounds());
	
		for (var i = 0; i < noise_description.length; i++) 
		{
			overlays['<i style="background:' + getColor(i) + '"></i> ' +noise_description[i]] = layers[i];
		}

		// Add layer control using above object
		layer = L.control.layers(null,overlays).addTo(map);
	}});
}

// Cleans the map current markers and control 
function cleanMap()
{
    for (var i = 0; i < layers.length; i++) 
	{
		map.removeLayer(layers[i]);
	}
	if (Object.keys(overlays).length)
		layer.removeFrom(map);
}

// Gets the color of a specific noise descriptor
function getColor(d) 
{
	return marker_colors[d];
}

// Defines the marker style for each marker
function marker_style(i) 
{
	return {
		fillColor: getColor(i),
		radius: 5,
		weight: 1,
		opacity: 1,
		color: 'white',
		dashArray: '3',
		fillOpacity: 0.7
	};
}


