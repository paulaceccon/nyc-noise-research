var datearray = [];
var colorrange = [];

function chart(csvpath, color) {

	if (color == "blue") {
	  colorrange = ["#045A8D", "#2B8CBE", "#74A9CF", "#A6BDDB", "#D0D1E6", "#F1EEF6"];
	}
	else if (color == "pink") {
	  colorrange = ["#980043", "#DD1C77", "#DF65B0", "#C994C7", "#D4B9DA", "#F1EEF6"];
	}
	else if (color == "orange") {
	  colorrange = ["#B30000", "#E34A33", "#FC8D59", "#FDBB84", "#FDD49E", "#FEF0D9"];
	}
	
	strokecolor = colorrange[0];

	var format = d3.time.format("%m/%d/%y");

	var mapPlotHeight = parseInt(d3.select("#map").style("height"));
	var mapPlotHeight = parseInt(d3.select("#map").style("height"));
	var sidebarWidth = parseInt(d3.select("#sidebar").style("width"));
	var streamPlotMargin = {top: 20, right: 30, bottom: 30, left: 30};
	var streamPlotWidth = document.body.clientWidth - streamPlotMargin.left - streamPlotMargin.right - sidebarWidth;
	var streamPlotHeight = 200 - streamPlotMargin.top - streamPlotMargin.bottom;
	
	var tooltip = d3.select("body")
		.append("div")
		.attr("class", "remove")
		.style("position", "absolute")
		.style("z-index", "20")
		.style("visibility", "hidden")
		.style("top", mapPlotHeight + 50 + streamPlotMargin.top + "px") // 50 of nav top
		.style("left", sidebarWidth + 80 + "px");

	var x = d3.time.scale()
		.range([0, streamPlotWidth]);

	var y = d3.scale.linear()
		.range([streamPlotHeight-10, 0]);

	var z = d3.scale.ordinal()
		.range(colorrange);

	var xAxis = d3.svg.axis()
		.scale(x)
		.orient("bottom")
		.ticks(d3.time.weeks);

	var yAxis = d3.svg.axis()
		.scale(y);

	var yAxisr = d3.svg.axis()
		.scale(y);

	var stack = d3.layout.stack()
		.offset("silhouette")
		.values(function(d) { return d.values; })
		.x(function(d) { return d.date; })
		.y(function(d) { return d.value; });

	// Group by key
	var nest = d3.nest()
		.key(function(d) { return d.key; })

	var area = d3.svg.area()
		.interpolate("cardinal")
		.x(function(d) { return x(d.date); })
		.y0(function(d) { return y(d.y0); })
		.y1(function(d) { return y(d.y0 + d.y); });
	    
	var svg = d3.select(".chart").attr("align","center")
		.append("svg")
    	.attr("width", streamPlotWidth)
    	.attr("height", streamPlotHeight + streamPlotMargin.top + streamPlotMargin.bottom)
  		.append("g")
    	.attr("transform", "translate(" + streamPlotMargin.left + "," + streamPlotMargin.top + ")");
    
	var graph = d3.csv(csvpath, function(data) {
	  data.forEach(function(d) {
		d.date = format.parse(d.date);
		d.value = +d.value;
	  });
// 	  console.log(data);

	  var layers = stack(nest.entries(data));

	  x.domain(d3.extent(data, function(d) { return d.date; }));
	  y.domain([0, d3.max(data, function(d) { return d.y0 + d.y; })]);

	  svg.selectAll(".layer")
		  .data(layers)
		  .enter().append("path")
		  .attr("class", "layer")
		  .attr("d", function(d) { return area(d.values); })
		  .style("fill", function(d, i) { return z(i); });

	  svg.append("g")
		  .attr("class", "x axis")
		  .attr("transform", "translate(0," + streamPlotHeight + ")")
		  .call(xAxis);

	  svg.append("g")
		  .attr("class", "y axis")
		  .call(yAxis.orient("left"));

	  svg.selectAll(".layer")
		.attr("opacity", 1)
		.on("mouseover", function(d, i) {
		  svg.selectAll(".layer").transition()
		  .duration(250)
		  .attr("opacity", function(d, j) {
			return j != i ? 0.6 : 1;
		})})

		.on("mousemove", function(d, i) {
		  mousex = d3.mouse(this);
		  mousex = mousex[0];
		  var invertedx = x.invert(mousex);
		  invertedx = invertedx.getMonth() + invertedx.getDate();
		  var selected = (d.values);
		  for (var k = 0; k < selected.length; k++) {
			datearray[k] = selected[k].date
			datearray[k] = datearray[k].getMonth() + datearray[k].getDate();
		  }

		  mousedate = datearray.indexOf(invertedx);
		  pro = d.values[mousedate].value;

		  d3.select(this)
		  	.classed("hover", true)
		  	.attr("stroke", strokecolor)
		  	.attr("stroke-width", "0.5px"), 
		  	tooltip.html( "<p>" + d.key + "<br>" + pro + "</p>" ).style("visibility", "visible");
	  
		})
		.on("mouseout", function(d, i) {
		 	svg.selectAll(".layer")
		  		.transition()
		 		.duration(250)
		  		.attr("opacity", "1");
		  		d3.select(this)
		  		  .classed("hover", false)
		  		  .attr("stroke-width", "0px"), tooltip.html( "<p>" + d.key + "<br>" + pro + "</p>" ).style("visibility", "hidden");
	  })

	  var vertical = d3.select(".chart")
			.append("div")
			.attr("class", "remove")
			.style("position", "absolute")
			.style("z-index", "19")
			.style("width", "1px")
			.style("height", "200px")
			.style("top", mapPlotHeight + streamPlotMargin.bottom)
			.style("bottom", "0px")
			.style("left", "0px")
			.style("background", "#fff");

	  d3.select(".chart")
		  .on("mousemove", function(){  
			 mousex = d3.mouse(this);
			 mousex = mousex[0] + 5;
			 vertical.style("left", mousex + "px" )})
		  .on("mouseover", function(){  
			 mousex = d3.mouse(this);
			 mousex = mousex[0] + 5;
			 vertical.style("left", mousex + "px")});
	});
}