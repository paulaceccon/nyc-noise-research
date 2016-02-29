import os
import glob

import numpy
import urllib2, json, csv
import itertools
from multiprocessing.pool import ThreadPool

from shapely.geometry import shape, Point
from rtree import index
from datetime import datetime, date, timedelta
from haversine import haversine


###################----------- Utils -----------###################
def saveDict(dict, output):
    """
    Save a dictionary as .csv.
    : param dict: {key : value}.
    : param output: output file name.
    """
    with open(output, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=';')
        for key, value in dict.iteritems():
            spamwriter.writerow([key, value])


def roundTime(dt=None, roundTo=60):
   """
   Round a datetime object to any time laps in seconds
   :param dt: datetime.datetime object, default now.
   :param roundTo: closest number of seconds to round to, default 1 minute.
   :return: the rounded time.
   """
   if dt == None : dt = datetime.now()
   seconds = (dt - dt.min).seconds
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   return dt + timedelta(0, rounding-seconds, -dt.microsecond)


def calculateEdgesDistance(edges, nodes):
    """
    Calculate the distance between two points.
    :param edges: an array of nodes long/lat (tuples) that correspond to edges.
    :param nodes: an array of long/lat (tuples) that corresponds to nodes.
    :return: a dictionary {pair of nodes : the distance between them}
    """
    dict = {}

    for edge in edges:
        node_1 = edge[0]
        node_2 = edge[1]
        dict[(nodes[node_1], nodes[node_2])] = haversine(nodes[node_1], nodes[node_2])

    return dict
    

def parseDate(date):
	DATE_FORMATS = ['%Y-%m-%d', '%m/%d/%Y %H:%M:%S', '%m/%d/%Y %I:%M:%S %p']
	for date_format in DATE_FORMATS:
		try:
			parsed = datetime.strptime(date, date_format)
		except ValueError:
			pass
		else:
			break
	else:
  		parsed = None
  	return parsed
  	
  	
def csvToList(filename):
	with open(filename, 'rb') as f:
		reader = csv.reader(f)
		next(reader, None)
		return list(reader)
		

###################----------- Base Data -----------###################
def getRegions():
    """
    Get the community districts of NY.
    :return: dictionary { region id : coordinates}.
    """
    dict = {}

    url = "https://nycdatastables.s3.amazonaws.com/2013-08-19T18:22:23.125Z/community-districts-polygon.geojson"
    response = urllib2.urlopen(url)
    data = json.loads(response.read(), strict=False)
    for district in data['features']:
        # (long, lat)
        dict[district['id']] = shape(district['geometry'])

    return dict


def getRoadsTopology():
    """
    Reads the nodes/edges of the NYC roads.
    :return: a list of nodes, and edges, both as tuples (long, lat).
    """
    nodes = []
    edges = []

    with open("../Resources/road.geojson") as data_file:
        data = json.loads(data_file.read(), strict=False)

    for road in data['features']:
        n_index = len(nodes)
        # (long, lat)
        coordinates = road['geometry']['coordinates'][0]
        for i in range(0, len(coordinates)):
            lat_long = coordinates[i]
            nodes.append((lat_long[0], lat_long[1]))

        for i in range(n_index, len(nodes) - 1):
            edges.append((i, i + 1))

    return nodes, edges


def getTaxiTrips(path):
    """
    Gets the taxi trips occurred in NY in 2015.
    :param date: (Y-m-d).
    :return: dict {key: [(long, lat, drop off date)]}.
    """
    taxi_dropoffs_per_region_time = numpy.zeros((149, 24))
    for filename in glob.glob(os.path.join(path, '*.csv')):
        taxi_dropoffs = consumeTaxiData(filename)
        taxi_dropoffs_per_region, taxi_dropoffs_per_region_points = taxiDropoffsPerRegion(regions_bbox, taxi_dropoffs)

        for key, value in taxi_dropoffs_per_region_points.iteritems():
            for item in value:
                taxi_dropoffs_per_region_time[int(key), item[2]] += 1
    return taxi_dropoffs_per_region_time


def consumeTaxiData(filename):
    """
    Given a url, reads its content and process its data.
    :param url: the url to be readen.
    :return: a list of tuples in the form (long, lat, hour).
    """
    print "Processing", filename
    points = []

    with open(filename, 'rb') as csvfile:
        data = csv.DictReader(csvfile, delimiter=',')
        for line in data:
            latitude = line.get('dropoff_latitude', None)
            if latitude is None:
                latitude = line.get('Dropoff_latitude', None)

            longitude = line.get('dropoff_longitude', None)
            if longitude is None:
                longitude = line.get('Dropoff_longitude', None)

            time = line.get('tpep_dropoff_datetime', None)
            if time is None:
                time = line.get('Lpep_dropoff_datetime', None)

            if time is not None:
                time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                if latitude is not None and longitude is not None and \
                        time.weekday():
                    time = roundTime(time, roundTo=60 * 60).hour
                    points.append((float(longitude), float(latitude), time))

    print len(points), "taxi trips"
    return points


def adjacencyMatrix(polyDict):
    """
    Defines regions are adjacent to each other.
    :param polyDict: dictionary {region id : polygon}.
    :return: 2D numpy array of regions (1, if there is intersection between regions).
    """
    regions_adjacency = numpy.zeros((149, 149))

    polygons = []
    # Populate R-tree index with bounds of polygons
    idx = index.Index()
    for p in polyDict.keys():
        polygon = shape(polyDict[p])
        idx.insert(int(p), polygon.bounds)

    for p in polyDict.keys():
        polygon = shape(polyDict[p])
        neighbors = list(idx.nearest(polygon.bounds))
        regions_adjacency[int(p), neighbors] = 1
        print p, neighbors

    return regions_adjacency
    
    
def filterPermits(dateIni, dateEnd):
    """
    Filters a .csv permit file.
    :return: a filtered .csv.
    """
    with open("../Resources/Multi_Agency_Permits.csv", 'rb') as fin, open("../Resources/Permiters.csv", 'wb') as fout:
        fieldnames = ['Longitude_WGS84', 'Latitude_WGS84', 'Permit_Issuance_Date', 'Permit_Type_Description']
        reader = csv.DictReader(fin, delimiter=',')
    	writer = csv.DictWriter(fout, fieldnames=fieldnames, delimiter=',')
    	writer.writeheader()
        for row in reader:
        	time = parseDate(row['Permit_Issuance_Date'])
        	if time and row['Longitude_WGS84'] and row['Latitude_WGS84'] and dateEnd >= time >= dateIni:
        		writer.writerow({k: row[k] for k in fieldnames if k in row})
        		
        		
def filterComplaints(dateIni, dateEnd):
    """
    Filters a .csv 311 complaints file.
    :return: a filtered .csv.
    """
    with open("../Resources/311_Service_Requests_from_2010_to_Present.csv", 'rb') as fin, open("../Resources/Complaints.csv", 'wb') as fout:
        fieldnames = ['Longitude', 'Latitude', 'Created Date', 'Descriptor']
        reader = csv.DictReader(fin, delimiter=',')
    	writer = csv.DictWriter(fout, fieldnames=fieldnames, delimiter=',')
    	writer.writeheader()
        for row in reader:
        	time = parseDate(row['Created Date'])
        	if time and dateEnd >= time >= dateIni:
        		writer.writerow({k: row[k] for k in fieldnames if k in row})        		


###################----------- Data Per Region -----------###################
def pointInPolygon(polyDict, points):
    """
    Defines which points are inside which regions.
    :param polyDict: dictionary {region id : polygon}.
    :param points: list of tuples (long, lat).
    :return: dictionaries {region id : number of points} and {region id : points}.
    """
    dict_count = {}
    dict_points = {}

    polygons = []
    # Populate R-tree index with bounds of polygons
    idx = index.Index()
    for pos, poly in enumerate(polyDict):
        dict_count[poly] = 0
        dict_points[poly] = []
        polygon = shape(polyDict[poly])
        polygons.append(polygon)
        idx.insert(pos, polygon.bounds)

    for i, p in enumerate(points):
    	try:
        	point = Point(float(p[0]), float(p[1]))
        except:
        	pass
        # Iterate through spatial index
        for j in idx.intersection(point.coords[0]):
            if point.within(polygons[j]):
                dict_count[j] += 1
                dict_points[j].append(p)

    return dict_count, dict_points


def roadsNodesPerRegion(regions, nodes):
    """
    Defines which road nodes falls in which regions.
    :param regions: dictionary {region id : polygon}.
    :param nodes: list of tuples (long, lat).
    :return: dictionaries {region id : number of road nodes} and {region id : roads nodes' coordinates}.
    """
    return pointInPolygon(regions, nodes)


def taxiDropoffsPerRegion(regions, taxi_dropoffs):
    """
    Defines which dropoffs falls in which regions.
    :param regions: dictionary {region id : polygon}.
    :param taxi_dropoffs: list of tuples (long, lat, hour).
    :return: dictionaries {region id : number of taxi dropoffs} and {region id : taxi dropoffs' coordinates}.
    """
    return pointInPolygon(regions, taxi_dropoffs)


def roadsLenghtPerRegion(nodes_per_region_points, edges, nodes):
    """
    Obtain the total length of road bed per region.
    :param nodes_per_region_points: dictionary {region id : list of nodes as tuples (long, lat)}.
    :param edges: list of edges (index) between nodes.
    :param nodes: list of tuples (long, lat).
    :return: dictionary {region id : total roads length}.
    """
    dict = {}

    edges_distance = calculateEdgesDistance(edges, nodes)
    for key, value in nodes_per_region_points.iteritems():
        dict[key] = 0
        combs = itertools.permutations(value, 2)
        for comb in combs:
            dist = edges_distance.get(comb, None)
            if dist is not None:
                dict[key] += dist

    return dict
    
def complaintsPerRegion(regions, complaints):
    """
    Defines which road nodes falls in which regions.
    :param regions: dictionary {region id : polygon}.
    :param nodes: list of tuples (long, lat).
    :return: dictionaries {region id : number of road nodes} and {region id : roads nodes' coordinates}.
    """
    return pointInPolygon(regions, nodes)


if __name__ == '__main__':
    # Geographical Features
    regions_bbox = getRegions()
    regions_number = len(regions_bbox)
    print "-----> Number of regions:", regions_number

    # print "-----> Processing road bed..."
    # nodes, edges = getRoadsTopology()
    # print "Nodes:", len(nodes)
    # print "Edges:", len(edges)

    # nodes_per_region_number, nodes_per_region_points = roadsNodesPerRegion(regions_bbox, nodes)
    # roads_length_per_region = roadsLenghtPerRegion(nodes_per_region_points, edges, nodes)
    # saveDict(nodes_per_region_number, "NodesPerRegion.csv")
    # saveDict(roads_length_per_region, "RoadLengthPerRegion.csv")

    # print "-----> Getting taxi data..."
    # pool = ThreadPool(2)
    # results = pool.map(getTaxiTrips, ['../Resources/tripdata/green', '../Resources/tripdata/yellow'])
    # pool.close()
    # pool.join()
    #
    # a = results[0]
    # b = results[1]
    #
    # numpy.savetxt("TaxiDropoffsPerRegion.csv", a+b, fmt='%i', delimiter='\t')

    # print "-----> Generating adjacenty matrix..."
    # regions_adjacency = adjacencyMatrix(regions_bbox)
    # numpy.savetxt("AdjacencyMatrix.csv", regions_adjacency, fmt='%i', delimiter='\t')
    
    print "-----> Filtering permits..."
    date_ini = datetime(2015, 01, 01)
    date_end = datetime(2015, 12, 31)
#     filterPermits(date_ini, date_end)
#     filterComplaints(date_ini, date_end)
    
    permits = csvToList("../Resources/Permiters.csv")
    complaints = csvToList("../Resources/Complaints.csv")
    
    permits_count, permits_points = pointInPolygon(regions_bbox, permits)
    complaints_count, complaints_points = pointInPolygon(regions_bbox, complaints)
    
    saveDict(permits_points, "../Resources/Permiters_Per_Region.csv")
    saveDict(complaints_points, "../Resources/Complaints_Per_Region.csv")    
    
    
