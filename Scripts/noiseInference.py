import urllib2, json, csv
import numpy
import requests
import itertools
import foursquare
import calendar
import datetime
import time

from shapely.geometry import shape, Point
from rtree import index
from datetime import datetime, date, timedelta
from haversine import haversine

###################----------- Utils -----------###################
def readJson(url):
    """
    Returns a json file specified in @url.
    """
    response = urllib2.urlopen(url)
    return json.loads(response.read())


def readCSV(url):
    """
    Returns a csv file specified in @url.
    """
    response = urllib2.urlopen(url)
    return csv.DictReader(response, delimiter=',')


###################----------- Base Data -----------###################
def getRegions():
    """
    Returns a dictionary formed by the id of a region and its coordinates.
    """
    dict = {}

    url = "https://nycdatastables.s3.amazonaws.com/2013-08-19T18:22:23.125Z/community-districts-polygon.geojson"
    data = readJson(url)
    for district in data['features']:
    	# (long, lat)
        dict[district['id']] = district['geometry']

    return dict
    
    
def getRoadsNodesAndEdges():
	"""
	Reads the nodes/edges of the NYC roads, returning a list of tuples of (long, lat).
	"""
	nodes = []
	edges = []
	
	f = open('../Resources/road-network.txt', 'r')
	nodes_edges = f.readline().split()
	nodes_number = int(nodes_edges[0])
	edges_number = int(nodes_edges[1])

	for line in range(nodes_number):
		lat_long = f.readline().split()
		nodes.append((float(lat_long[1]), float(lat_long[0])))
	
	for line in range(edges_number):
		n_n = f.readline().split()
		edges.append((int(n_n[0]), int(n_n[1])))
	f.close()
	
	return nodes, edges
	

def getPOIs():
    """
    Returns a list of tuples of POIs lat/long coordinates.
    """
    urls = ["https://nycdatastables.s3.amazonaws.com/2013-06-04T18:02:56.019Z/museums-and-galleries-results.csv",
            "https://nycdatastables.s3.amazonaws.com/2013-12-16T21:49:55.716Z/nyc-parking-facilities-results.csv",
            "https://nycdatastables.s3.amazonaws.com/2013-06-20T16:06:05.136Z/mapped-in-ny-companies-results.csv",
            "https://nycdatastables.s3.amazonaws.com/2013-06-11T18:59:27.269Z/nyc-public-school-locations-results.csv",
            "https://nycdatastables.s3.amazonaws.com/2013-07-29T15:49:03.498Z/nyc-private-school-results.csv",
            "https://nycdatastables.s3.amazonaws.com/2013-07-01T16:25:00.297Z/nyc-special-education-school-results.csv",
            "https://nycdatastables.s3.amazonaws.com/2013-06-05T14:35:56.387Z/basic-description-of-colleges-and-universities-results.csv",
            "https://nycdatastables.s3.amazonaws.com/2013-06-05T20:25:17.301Z/operating-sidewalk-cafes-results.csv",
            "https://nycdatastables.s3.amazonaws.com/2013-06-04T14:40:48.764Z/community-health-centers-results.csv",
            "http://data.nycprepared.org/ar/dataset/dycd-after-school-programs-housing/resource/d2306a8f-59d1-4cb0-b527-ba44ca8eec3a",
            "http://data.nycprepared.org/ar/dataset/dycd-after-school-programs-family-support-programs-for-seniors/resource/493f52a4-0a49-4f5f-8937-78e69fb77852",
            "https://nycdatastables.s3.amazonaws.com/2013-07-02T15:29:20.692Z/agency-service-center-results.csv",
            "https://nycdatastables.s3.amazonaws.com/2013-06-13T18:39:44.536Z/nyc-2012-farmers-market-list-results.csv",
            "https://nycdatastables.s3.amazonaws.com/2013-10-18T21:14:52.348Z/nyc-grocery-stores-final.csv",
            "https://nycdatastables.s3.amazonaws.com/2013-06-18T14:29:37.626Z/subway-entrances-results.csv",
            "https://nycdatastables.s3.amazonaws.com/2013-06-04T17:58:59.335Z/map-of-monuments-results.csv",
            "https://nycdatastables.s3.amazonaws.com/2013-06-18T20:17:34.010Z/nyc-landmarks-results.csv"]

    POIs = []

    for url in urls:
        csv = readCSV(url)
        print url
        for line in csv:
            latitude = line.get('latitude', None)
            longitude = line.get('longitude', None)
            if latitude is not None and longitude is not None:
                POIs.append((float(longitude), float(latitude)))

    return POIs
    

def getEdgesDistance(edges, nodes):
	"""
	Returns a dictionary formed by a pair of nodes and the distance between them.
	@edges an array of the nodes (tuples) that correspond to edges
	@nodes an array of long/lat (tuples).
	"""
	dict = {}
	
	for edge in edges:
		node_1 = edge[0]
		node_2 = edge[1]
		dict[(nodes[node_1], nodes[node_2])] = haversine(nodes[node_1], nodes[node_2])
		
	return dict    
    

def get311NoiseComplaints(date):	
	"""
	Given a @date (Y-m-d), returns a dictionary formed by complaint descriptor and the 
	number complaints of this type.
	"""
	query_string = "http://data.cityofnewyork.us/resource/fhrw-4uyv.json"
	query_string += "?"                                                   
	query_string += "$where="                                            
	query_string += "(complaint_type like '%Noise%')"
	query_string += " AND "
	query_string += "(created_date>='" + date + "')"
	query_string += "&$group=descriptor,latitude,longitude"
	query_string += "&$select=descriptor,latitude,longitude"
	
	print query_string
	result = requests.get(query_string).json()
	
	# Dictionary of complaints
	complaints = {'Air Condition/Ventilation Equipment' : 0, 'Alarms' : 0, 
				  'Banging/Pounding' : 0, 'Barking Dog' : 0, 'Car/Truck Horn' : 0, 
				  'Car/Truck Music' : 0, 'Construction Equipment' : 0,
				  'Construction Before/After Hours' : 0, 'Engine Idling' : 0, 
				  'Ice Cream Truck' : 0, 'Jack Hammering' : 0, 'Lawn Care Equipment' : 0, 
				  'Loud Music/Party' : 0, 'Loud Talking' : 0, 'Loud Television' : 0, 
				  'Manufacturing Noise' : 0, 'Private Carting Noise' : 0, 'Others' : 0}
				   
	for record in result:
		for key in complaints:
			if key.find(record.get('descriptor')) > -1:
				complaints[key] += 1
				break
			elif key == "Others":
				complaints[key] += 1	
				

def getFoursquareCheckIns(date):
	"""
	Given a @date (Y-m-d), returns a dictionary formed by (lat, long) and the number 
	of check-ins in the spot located at this coordinate.
	"""
	client = foursquare.Foursquare(client_id='FUG50WOUTS2FHTCUIVFUUXFFTUGGIC1CITI53KBXPAVDFDV0', 
							       client_secret='2BLM42NTYGLNAA0J3ECOZSHJVJ0ZBC1S32MWBF24JWDN5PIX')
	auth_uri = client.oauth.auth_url()	
	time_since_epoch = time.mktime(time.strptime(date, "%Y-%m-%d"))
	checkins = client.venues.explore(params={'near': 'New York, NY', 'afterTimestamp' : date})
	
	dict = {}
	
	for checkin in checkins['groups']:
		for item in checkin['items']:
			lat = item['venue']['location']['lat']
			lng = item['venue']['location']['lng']
			cic = item['venue']['stats']['checkinsCount']
			dict[(lng, lat)] = cic
			
	return dict

    
###################----------- Data Per Region -----------###################
def pointInPolygon(polyDict, points):
	"""
	Given a dictionary (@polyDict) of id : polygon and a list of points (as tuples),
	returns a dictionary id : number of points inside polygon.
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
  		point = Point(p[0], p[1])
  		# Iterate through spatial index
  		for j in idx.intersection(point.coords[0]):
  			if point.within(polygons[j]):
  				dict_count[j] += 1
  				dict_points[j].append(p)	
  	
  	return dict_count, dict_points

def POIsPerRegion(regions, POIs):
    """
    Returns a dictionary formed by the id of a region and the number of POIs that falls in
    this region.
    @regions is a dictionary in the form id : region shape
    @POIs is a list of tuples (long, lat)
    """
    return pointInPolygon(regions, POIs)

        
def roadsNodesPerRegion(regions, nodes):
	"""
	Returns a dictionary formed by the id of a region and the number of nodes that falls in
	this region.
	@regions is a dictionary in the form id : region shape
	@nodes is a list of tuples (long, lat)
	"""
	return pointInPolygon(regions, nodes)
	
	
def roadsLenghtPerRegion(nodes_per_region_points, edges, nodes):
	"""
	Returns a dictionary formed by the id of a region and the total length of edges
	that falls in this region.
	@nodes_per_region_points is a dictionary in the form id : number of nodes
	@edges is a list of edges between @nodes
	"""
	dict = {}
	
	edges_distance = getEdgesDistance(edges, nodes)
	for key, value in nodes_per_region_points.iteritems():
		dict[key] = 0
		combs = itertools.permutations(value, 2)
		for comb in combs:
			dist = edges_distance.get(comb, None)
			if dist is not None:
				dict[key] += dist
				
	return dict
	
	
def checkinsPerRegion(regions, checkins):

	dict = {}
	
	spots_per_region_number, spots_per_region_points = pointInPolygon(regions, checkins.keys())
	for key, value in spots_per_region_points.iteritems():
		dict[key] = 0
		for v in value:
			dict[key] += checkins[v]
	
	return dict
				
		
	
if __name__ == '__main__':
	# Yesterday's date
	date = str(datetime.date(datetime.now()) - timedelta(1))
	
	# Geographical Features
	regions_bbox = getRegions()
	regions_number = len(regions_bbox)
	print "Regions:", regions_number

    print "Reading POIs..."
    POIs = getPOIs()
    print "POIs:", len(POIs)
#     print "Done Reading POIs"

    print "Calculating POIs per Region"
    POIsPerRegion = POIsPerRegion(regions_bbox, POIs)
#     print POIsPerRegion
    
    nodes, edges = getRoadsNodesAndEdges()
    print "Nodes:", len(nodes)
    print "Edges:", len(edges)
    
    print "Calculating nodes per Region"
    nodes_per_region_number, nodes_per_region_points = roadsNodesPerRegion(regions_bbox, nodes)
#     print nodes_per_region_number
    
    roads_lenght_per_region = roadsLenghtPerRegion(nodes_per_region_points, edges, nodes)
#     print roads_lenght_per_region
    
    print "Getting noise complaints"
    get311NoiseComplaints(date)

	print "Getting Foursquare check-ins"
	checkins = getFoursquareCheckIns(date)
	
	print "Calculating check-ins per Region"
	checkins_per_region = checkinsPerRegion(regions_bbox, checkins)
# 	print checkins_per_region
    