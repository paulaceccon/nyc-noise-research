/* Map definition */
	
// Map reference
var map;

// Geojson of the neighborhoods reference
var geojson;

// States info
var info;

// Noise inference data
var noiseMap = {};
var noiseMapMatrix;
var totalNoisePerRegion;
var legend;

regions_count = 149;
complaints_type = 18;
time_slots = 24;

var lower_time = 0;
var upper_time = 23;

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
function buildNoiseMatrix(dict)
{
	var data = new Array(regions_count);
	for (i = 0; i < regions_count; i++)
	{
		data[i] = new Array(complaints_type);
		for (j = 0; j < complaints_type; j++)
		{
			data[i][j] = new Array(time_slots);
			for (k = 0; k < time_slots; k++)
			{
				data[i][j][k] = 0.0;
			}
		}
	}
	
	for (var key in dict)
	{
		k = key.split('-')[1].split('.')[0];
		m = dict[key];
		for (i = 0; i < regions_count; i++)
		{
			for (j = 0; j < complaints_type; j++)
			{
				data[i][j][k] += parseFloat(m[i][j]);
			}
		}
	}
	noiseMapMatrix = data;
}

function countNoisePerRegion(lower_bound, upper_bound)
{
	var noisePerRegion = [];
	for (i = 0; i < regions_count; i++)
	{
		var count = 0;
   		for (j = 0; j < complaints_type; j++)
    	{   
        	for (k = lower_bound; k < upper_bound+1; k++)
        	{
            	count += noiseMapMatrix[i][j][k];
        	}
   	 	}
   	 	noisePerRegion.push(count);
   	 }
   	 
   	 totalNoisePerRegion = noisePerRegion;
}

// Parse the .csv files
function parseNoiseInferenceFiles(files)
{
	var noise = {}
	$("input[type=file]").parse({
		config: {
		complete: function(results, file) {
// 						console.log("This file done:", file['name'], results);
						noise[file['name']] = results.data;
				  }
		},
		complete: function() {
			console.log("All files done!");
			if (!_.isEmpty(noise))
			{
				noiseMap = noise;
				buildNoiseMatrix(noiseMap);
				refreshData(0, 23);
			}
		}
	});
}


function refreshData(lower_bound, upper_bound)
{
	lower_time = lower_bound;
	upper_time = upper_bound;
	if (!_.isEmpty(noiseMapMatrix))
	{
		countNoisePerRegion(lower_time, upper_time);
		fillStyle();
	}
}

// Returns the noise data per region
function getNoisePerRegion()
{
	return noiseMap;
}


// Loads GeoJSON community districts from an external file
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
		this._div.innerHTML = (props && !_.isEmpty(totalNoisePerRegion) ? '<b> Region ID: '+ props.id +' </b><br />' + 'Complaints: ~'+ Math.round(totalNoisePerRegion[props.id]) + '<br />2015-06-10 / 2015-01-13<br />' : 'No available data.');
		if (props && !_.isEmpty(noiseMapMatrix))
		{
			pieChart(noiseMapMatrix, props.id, lower_time, upper_time);
			stackedbarchart(noiseMapMatrix, props.id);
		}
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
		fillColor: getComplaintsCountColor(feature.id, true),
		weight: 1,
		opacity: 1,
		color: 'white',
		dashArray: '3',
		fillOpacity: 0.7
	};
}

function fillStyle()
{
	geojson.eachLayer(function (layer) {    
    	layer.setStyle(style(layer.feature)) 
	});
	
	// Legend of the states' color
	if (_.isEmpty(legend))
	{
		legend = L.control({position: 'bottomleft'});
	
		legend.onAdd = function (map) 
		{
			var div = L.DomUtil.create('div', 'info legend'),
				grades = [0, 10, 20, 50, 100, 200],
				labels = [];

			for (var i = 0; i < grades.length; i++) {
				div.innerHTML +=
					'<div style="background:' + getComplaintsCountColor(grades[i] + 1, false) + '; border-radius: 50%; width: 10px; height: 10px; display:inline-block;"></div> ' +
					grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
			}

			return div;
		};
		legend.addTo(map);
	}
}

function getComplaintsCountColor(d, id) 
{
	if (id)
	{	
		if (!_.isEmpty(totalNoisePerRegion))
			d = totalNoisePerRegion[d]; 
		else 	
			return 'white';
	}
    return d > 400  ? '#800026' :
           d > 300  ? '#BD0026' :
           d > 200  ? '#E31A1C' :
           d > 100  ? '#FC4E2A' :
           d > 50   ? '#FD8D3C' :
           d > 20   ? '#FEB24C' :
           d > 10   ? '#FED976' :
                      '#FFEDA0';
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
// 	d3.selectAll(".piechart").style("opacity", 0);
	info.update();
}

// Defines the behavior when a neighborhood 
// is clicked
function zoomToFeature(e) 
{
	map.fitBounds(e.target.getBounds());
}