function stackedbarchart(wholeData, regionId)
{

	var jsonArr = [];
	var colorrange = _.values(getNoiseDescriptorsColors());
	var descriptors = _.keys(getNoiseDescriptorsColors());
	for (j = 0; j < complaints_type; j++)
	{	
		complaint = []
		for (k = 0; k < time_slots; k++)
		{
			var count = wholeData[regionId][j][k];
			complaint.push({
				"name": descriptors[j],
				"label": k.toString(),
				"value": count,
			});		
		}
		jsonArr.push(complaint);
	}	
	data = jsonArr;
	
	var margin = 
	{
    	top: 10,
    	right: 10,
    	bottom: 40,
    	left: 60
  	},
  	legend = 250,
  	width = 500 - margin.left - margin.right,
  	height = 600 - margin.top - margin.bottom - legend;

	var color = d3.scale.ordinal()
	  .range(colorrange);

	var stack = d3.layout.stack()
	  .x(function(d, i) {
		return i;
	  })
	  .y(function(d) {
		return d.value;
	  });

	stack(data);

	var xScale = d3.time.scale()
	  .domain([new Date(0, 0, 0, data[0][0].label, 0, 0, 0), new Date(0, 0, 0, data[0][data[0].length - 1].label, 0, 0, 0)])
	  .rangeRound([0, width - margin.left - margin.right]);


	var yScale = d3.scale.linear()
	  .domain([0,
		d3.max(data, function(d) {
		  return d3.max(d, function(d) {
			return d.y0 + d.value;
		  });
		})
	  ])
	  .range([height - margin.bottom - margin.top, 0]);

	var xAxis = d3.svg.axis()
	  .scale(xScale)
	  .ticks(d3.time.hour, 1)
	  .tickFormat(d3.time.format("%H"));

	var yAxis = d3.svg.axis()
	  .scale(yScale)
	  .orient("left")
	  .ticks(10);

	var svg = d3.select(".info")
	  .attr("align","center")
	  .append("svg")
	  .attr("width", width)
	  .attr("height", height + legend);

	var groups = svg.selectAll("g")
	  .data(data)
	  .enter()
	  .append("g")
	  .attr("class", "rgroups")
	  .attr("transform", "translate(" + margin.left + "," + (height - margin.bottom) + ")")
	  .style("fill", function(d, i) {
		return colorrange[i];
	  });

	var rects = groups.selectAll("rect")
	  .data(function(d) {
		return d;
	  })
	  .enter()
	  .append("rect")
	  .attr("width", 8)
	  .attr("height", function(d) {
		return -yScale(d.value) + (height - margin.top - margin.bottom);
	  })
	  .attr("x", function(d) {
		return xScale(new Date(0, 0, 0, d.label, 0, 0, 0));;
	  })
	  .attr("y", function(d) {
		return -(-yScale(d.y0) - yScale(d.value) + (height - margin.top - margin.bottom) * 2);
	  })
	  .attr("data-legend",function(d) { return d.name; });

	svg.append("g")
	  .attr("class", "x axis")
	  .attr("transform", "translate(" + margin.left + "," + (height - margin.bottom) + ")")
	  .call(xAxis);


	svg.append("g")
	  .attr("class", "y axis")
	  .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
	  .call(yAxis);

	svg.append("text")
	  .attr("transform", "rotate(-90)")
	  .attr("y", 0 + 5)
	  .attr("x", 0 - (height / 2) - margin.top)
	  .attr("dy", "1em")
	  .text("Complaints");

	svg.append("text")
	  .attr("class", "xtext")
	  .attr("x", width / 2)
	  .attr("y", height - 5)
	  .attr("text-anchor", "middle")
	  .text("Hour of day");
	  
	legend = svg.append("g")
    	.attr("class","legend")
    	.attr("transform","translate("+ margin.left + "," + (height + margin.bottom/2) + ")")
    	.style("font-size","12px")
    	.call(d3.legend)
}