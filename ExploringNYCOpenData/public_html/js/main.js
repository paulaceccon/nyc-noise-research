/******** Map definition ********/
var map;        // Reference to the map
var info;       // Reference to info layer
var geojson;    // Reference to geojson that defines the districts 


/******** Data to be plotted ********/
var query_result_311;
var query_result_permits;

// ---- Data colors ---- //
var complaints_colors = {'Alarms': '#FA8072', 'Banging/Pounding': '#FF8C00', 'Car/Truck Horn': '#DB7093',
    'Engine Idling': '#FFD700', 'Construction Equipment': '#DC143C', 'Construction Before/After Hours': '#8B0000',
    'Jack Hammering': '#FF6347'};

var permits_colors = {'ALTERATION': '#4169E1', 'PLUMBING': '#00BFFF', 'EQUIPMENT WORK': '#87CEEB', 
    'EQUIPMENT': '#4682B4', 'FOUNDATION': '#48D1CC', 'NEW BUILDING': '#6A5ACD', 'SIGN': '#9370DB', 
    'FULL DEMOLITION': '#1E90FF'};

// ---- Map layers ---- //
var layers_311 = {};
var layer_311;
var overlays_311 = {};

var layers_permits = {};
var layer_permits;
var overlays_permits = {};

// ---- Points in Polygon ---- //
var points_311 = {};
var points_permits = {};