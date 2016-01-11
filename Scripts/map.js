/* Map definition */
	
// Map reference
var map;

// Geojson of the neighborhoods reference
var geojson;

// States info
var info;

// Noise inference data
var noiseMap = [];

// ---- Map Creation

// Creates a map inside div id="map"
function createMap()
{				
	// Create Leftlet map and center it in the desired position
	// with the desirable zoom level
	map = L.map('map').setView([40.658528, -73.952551], 10);

	// Load a tile layer  
	L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', 
	{ 
		attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a>',
		maxZoom: 18, 
		minZoom: 10
	}).addTo(map);
		
	return map;
}

//---- Map Interaction

// Loads noise inference results
function loadNoisePerRegion(files)
{
	regions_count = 149;
	complaints_type = 18;
	time_slots = 24;
	
	var data = new Array(regions_count);
	for (i = 0; i < regions_count; i++)
	{
		data[i] = new Array(complaints_type);
		for (j = 0; j < complaints_type; j++)
		{
			data[i][j] = new Array(time_slots);
		}
	}
	
	
}

function parseNoiseInferenceFiles(files)
{
	$("input[type=file]").parse({
		config: {
		complete: function(results, file) {
						console.log("This file done:", file, results);
						noiseMap.push(results)
				  }
		},
		complete: function() {
			console.log("All files done!");
			console.log(noiseMap);
		}
	});
}


// Loads GeoJSON from an external file
// function loadRoadMap()
// {
// 	$.ajax({async: false, dataType: "json", url: "https://data.cityofnewyork.us/api/geospatial/svwp-sbcd?method=export&format=GeoJSON", success: function(data)
// 	{
// 		// Add GeoJSON layer to the map once the file is loaded
// 		geojson = L.geoJson(data).addTo(map);
// 		count = 0;
// 		$(data.features).each(function(index, rec) 
// 		{
// 			if ( rec.hasOwnProperty("geometry") )
// 			{
// 				coordinates = rec['geometry']['coordinates'][0]
// 				for (i = 0; i < coordinates.length; i++)
// 				{
// 					count++;
// 					lat_long = coordinates[i];
// 					L.circleMarker([lat_long[1], lat_long[0]], roadPointsMarker()).addTo(map);
// 				}
// 			}
// 		});
// 	}});
// }
// 
// // Defines the marker style for each marker
// function roadPointsMarker() 
// {
// 	return {
// 		fillColor: '#f03',
// 		radius: 0.2
// 	};
// }

// Loads GeoJSON from an external file
function loadNeighborhoods()
{
	$.ajax({async: false, dataType: "json", url: "https://nycdatastables.s3.amazonaws.com/2013-08-19T18:22:23.125Z/community-districts-polygon.geojson", success: function(data)
	{
		// Add GeoJSON layer to the map once the file is loaded
		geojson = L.geoJson(data,  
		{
			style: style,
			onEachFeature: onEachFeature
		}).addTo(map);
	}});
	
    // Control that shows state info on hover
	info = L.control();

	info.onAdd = function (map) {
		this._div = L.DomUtil.create('div', 'info');
		this.update();
		return this._div;
	};

	info.update = function (props) {
		this._div.innerHTML = (props ? '<b> Region ID:'+ props.id +' </b><br />' : 'Hover over a state');
		if (props) pieChart();
	};

	info.addTo(map);
}

// Returns the neighborhoods
function getNeighborhoods()
{
	return geojson;	
}

// Defines the existent behaviors that
// each geojson feature will have
function onEachFeature(feature, layer) 
{
	layer.on({
		mouseover: highlightFeature,
		mouseout: resetHighlight,
		click: zoomToFeature
	});
}

// Defines the style of the neighborhoods' polygons
function style(feature) 
{
	return {
		fillColor: '#FFEDA0',
		weight: 1,
		opacity: 1,
		color: 'white',
		dashArray: '3',
		fillOpacity: 0.7
	};
}

// Defines the behavior of a neighborhood when 
// the mouse is over it 			
function highlightFeature(e) 
{
	var layer = e.target;

	layer.setStyle({
		weight: 3,
		color: '#666',
		dashArray: '',
		fillOpacity: 0.7
	});

	if (!L.Browser.ie && !L.Browser.opera) 
	{
		layer.bringToFront();
	}
	info.update(layer.feature);
}

// Resets the style of a neighborhood previous
// highlighted
function resetHighlight(e) 
{
	var layer = e.target;
	
	geojson.resetStyle(layer);
	if (!L.Browser.ie && !L.Browser.opera) 
	{
		layer.bringToBack();
	}
	d3.selectAll(".piechart").style("opacity", 0);
	info.update();
}

// Defines the behavior when a neighborhood 
// is clicked
function zoomToFeature(e) 
{
	map.fitBounds(e.target.getBounds());
}