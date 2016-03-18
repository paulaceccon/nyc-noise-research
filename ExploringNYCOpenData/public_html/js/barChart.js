/* global d3, complaints_colors, permits_colors, points_311, points_permits */

function barChart(type, region)
{
    if (type === '311')
    {
        colors = complaints_colors;
        dict = points_311;
    } else if (type === 'Permits')
    {
        colors = permits_colors;
        dict = points_permits;
    }

    if (!dict.hasOwnProperty(region))
        return;

    var data = [];
    for (var key in colors)
    {
        data.push({
            "label": key,
            "value": dict[region][key],
            "color": colors[key]
        });
    }

    var margin = {top: 20, right: 20, bottom: 100, left: 40},
    width = 300 - margin.left - margin.right,
            height = 250 - margin.top - margin.bottom;

    var x = d3.scale.ordinal()
            .rangeRoundBands([0, width], .1);

    var y = d3.scale.linear()
            .range([height, 0]);

    var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom");

    var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left")
            .ticks(10, "10");

    var svg = d3.select(".info").attr("align", "center").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    x.domain(data.map(function (d) {
        return d.label;
    }));
    y.domain([0, d3.max(data, function (d) {
            return d.value;
        })]);

    svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis)
            .selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "-.8em")
            .attr("dy", "-.55em")
            .attr("transform", "rotate(-40)");

    svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .text("Value");


    svg.selectAll(".bar")
            .data(data)
            .enter().append("rect")
            .attr("class", "bar")
            .attr("x", function (d) {
                return x(d.label);
            })
            .attr("width", x.rangeBand())
            .attr("y", function (d) {
                return y(d.value);
            })
            .attr("height", function (d) {
                return height - y(d.value);
            })
            .style("fill", function (d) {
                return d.color;
            });
}

function type(d)
{
    d.frequency = +d.frequency;
    return d;
}