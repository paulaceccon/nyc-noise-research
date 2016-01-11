// Given a json resulting from a 311 data request, constructs an array of dictionaries
// with the following structure: { hour : h, value : v, key : k}
function complaintsPerHour(data)
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
	return dict.__array;
}

function inferredComplaints(data)
{	
	regions_count = 149;
	complaints_type = 18;
	time_slots = 24;
	
	// regions_count x complaints_type
	var complaints_per_region = new Array(regions_count);
	for (i = 0; i < regions_count; i++)
	{
		complaints_per_region[i] = new Array(complaints_type);
		for (j = 0; j < complaints_type; j++)
		{
			complaints_per_region[i][j] = 0;
		}
	}
	
	for (i = 0; i < regions_count; i++)
	{
		for (j = 0; j < complaints_type; j++)
		{
			for (k = 0; k < time_slots; k++)
			{
				complaints_per_region[i][j] += data[i][j][k];
			}
		}
	}
		
	return complaints_per_region;
}


// https://www.mapbox.com/mapbox.js/example/v1.0.0/point-in-polygon/
function complaintsPerRegion(complaints_data)
{	
	var dict = {};
	var regions = getNeighborhoods();

    $.each(complaints_data, function(index, rec)
	{
		if ( rec.hasOwnProperty("latitude") && rec.hasOwnProperty("longitude") )
		{
			var layer = leafletPip.pointInLayer([rec.longitude , rec.latitude], regions, true);
		}
	});
}

