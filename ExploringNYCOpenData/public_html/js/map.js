/* global L */

// ---- Map Creation ---- //

// Creates a map inside div id="map"
function createMap()
{
    // Create a Leftlet map and center it in the desired position
    // with the desirable zoom level
    map = L.map('map').setView([40.658528, -73.952551], 11);
    map.setMaxBounds([[40.917577, -74.25909], [40.477399, -73.700009]]);

    // Load a tile layer  
    L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            {
                attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a>',
                maxZoom: 18,
                minZoom: 10
            }).addTo(map);
}

// Loads GeoJSON community districts from an external file
function loadDistricts()
{
    $.ajax({async: false, dataType: "json", url: "community-districts-polygon.geojson", success: function (data)
        {
            // Add GeoJSON layer to the map once the file is loaded
            geojson = L.geoJson(data,
                    {
                        style: style,
                        onEachFeature: onEachFeature
                    }).addTo(map);
        }});

    // Control that shows some info of a district when 
    // the mouse is over it
    info = L.control();

    info.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'info');
        this.update();
        return this._div;
    };
    
    info.update = function (props) {
        this._div.innerHTML = props ? '<b> Region ID: '+ props.id +'</b><br />' : 'No available data.';
        if (props)
        {
            barChart('311', props.id);
            barChart('Permits', props.id);
        }
    };

    info.addTo(map);
}

// Defines the style of the GeoJSON polygons
function style(feature)
{
    return {
//        fillColor: getComplaintsCountColor(feature.id, true),
        weight: 2,
        opacity: 1,
        color: 'gray',
        dashArray: '3',
        fillOpacity: 0.2
    };
}

// Defines behavior of each of the GeoJSON polygons
function onEachFeature(feature, layer)
{
    layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
        click: zoomToFeature
    });
}

// Defines the behavior of each of the GeoJSON polygons
// when the mouse is over them 			
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
        layer.bringToFront();
    
    info.update(layer.feature);
}

// Resets the style of a GeoJSON polygon that
// was previous highlighted
function resetHighlight(e)
{
    var layer = e.target;

    geojson.resetStyle(layer);
    if (!L.Browser.ie && !L.Browser.opera)
        layer.bringToBack();
    
    info.update();
}

// Defines the behavior of each of the GeoJSON polygon
// occurs a mouse click on them
function zoomToFeature(e)
{
    map.fitBounds(e.target.getBounds());
}