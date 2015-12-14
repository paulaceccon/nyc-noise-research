// Given a json resulting from a 311 data request, constructions an array of dictionaries
// with the following structure: { hour : h, value : v, key : k}
function complaints_per_hour(data)
{
	var jsonArr = [];
	$.each(data, function(index, rec)
	{
		if ( rec.hasOwnProperty("latitude") && rec.hasOwnProperty("longitude") )
		{
			var hour = new Date(rec.created_date).getHours();
// 			var hour = (hour == 0) ? 24 : hour;
			jsonArr.push({
				"hour": hour,
				"value": 1,
				"key": rec.descriptor
			});
		}
	});

	var desc_colors = getNoiseDescriptorsColors();
	var hours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
				 14, 15, 16, 17, 18, 19, 20, 21, 22, 23];
			
	var dict = {__array:[]};	
	for(var desc in desc_colors)
	{
		for (var d = 0; d < hours.length; d++)
		{
			var key = hours[d]+"|"+desc;
			if (!(key in dict))
			{
				dict.__array.push(dict[key] = {
					"hour": hours[d],
					"value": 0,
					"key": desc
				});
			}
		}
	}	
// 	console.log(dict.__array);
	$.each(jsonArr, function(index, rec)
	{
		var key = rec.hour+"|";
		// Building key accordingly to pre-defined keys
		for (var desc in desc_colors) 
		{
			if (rec.key.indexOf(desc) > -1) 
			{
				key += desc;
				break;
			}
			if (desc == "Others") 
			{
				key += desc;
			}
		}
		obj = dict[key];
		obj["value"] += 1;
		dict[key] = obj;
		
	});
// 	console.log(dict.__array);
	return dict.__array;
}


// https://www.mapbox.com/mapbox.js/example/v1.0.0/point-in-polygon/
function complaints_per_region(complaints_data)
{	
	var dict = {};
	var regions = getNeighborhoods();
	console.log(regions);
       //  L.marker([38, -102], {
//             icon: L.mapbox.marker.icon({
//                 'marker-color': '#f86767'
//             }),
//             draggable: true
//         }).addTo(map)
//         .on('dragend', function(e) {
//             
//             if (layer.length) {
//               state.innerHTML = '<strong>' + layer[0].feature.properties.name + '</strong>';
//             } else {
//               state.innerHTML = '';
//             }
//         });
    $.each(complaints_data, function(index, rec)
	{
		if ( rec.hasOwnProperty("latitude") && rec.hasOwnProperty("longitude") )
		{
			var layer = leafletPip.pointInLayer([rec.longitude , rec.latitude], regions, true);
// 			console.log(layer);
			// if (layer.length) {
//               state.innerHTML = '<strong>' + layer[0].feature.properties.name + '</strong>';
//             } else {
//               state.innerHTML = '';
//             }
		}
	});
}

