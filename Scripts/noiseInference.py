# https://data.cityofnewyork.us/City-Government/road/svwp-sbcd
# 28BBYCCUPYHWVFSSSD9Q
import urllib2, json, csv
import requests
import itertools
import foursquare

from shapely.geometry import shape, Point
from rtree import index
from datetime import datetime, date, timedelta
from haversine import haversine

# Custom
import tensorDecomposition


###################----------- Utils -----------###################
def readJson(url):
    """
    Read a json file.
    :param url: url to be read.
    :return: a json file.
    """
    try:
        response = urllib2.urlopen(url)
        return json.loads(response.read())
    except urllib2.HTTPError as e:
        return None


def readCSV(url):
    """
    Read a csv file.
    :param url: url to be read.
    :return: an array of dictionaries.
    """
    try:
        response = urllib2.urlopen(url)
        return csv.DictReader(response, delimiter=',')
    except urllib2.HTTPError as e:
        return None


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


###################----------- Base Data -----------###################
def getRegions():
    """
    Get the community districts of NY.
    :return: dictionary { region id : coordinates}.
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
    Reads the nodes/edges of the NYC roads.
    :return: a list of nodes, and edges, both as tuples (long, lat).
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
    Get some Points of Interests of NY.
    :return: list of tuples of POIs (long, lat).
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


def get311NoiseComplaints(date):
    """
    Gets all noise complaints of NY from a staring date.
    :param date: (Y-m-d).
    :return: dictionary {complaint type : total number of complaints of this type}
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
    complaints = {'Air Condition/Ventilation Equipment': 0, 'Alarms': 0,
                  'Banging/Pounding': 0, 'Barking Dog': 0, 'Car/Truck Horn': 0,
                  'Car/Truck Music': 0, 'Construction Equipment': 0,
                  'Construction Before/After Hours': 0, 'Engine Idling': 0,
                  'Ice Cream Truck': 0, 'Jack Hammering': 0, 'Lawn Care Equipment': 0,
                  'Loud Music/Party': 0, 'Loud Talking': 0, 'Loud Television': 0,
                  'Manufacturing Noise': 0, 'Private Carting Noise': 0, 'Others': 0}

    complaints_loc = {}
    for key in complaints:
        complaints_loc[key] = []

    for record in result:
        for key in complaints:
            if key.find(record.get('descriptor')) > -1:
                complaints[key] += 1
                complaints_loc[key].append((record.get('longitude'), record.get('latitude')))
                break
            elif key == "Others":
                complaints[key] += 1
                complaints_loc[key].append((record.get('longitude'), record.get('latitude')))

    return complaints, complaints_loc


def getFoursquareCheckIns(date):
    """
    Gets the check-ins occurred in NY from a starting date.
    :param date: (Y-m-d).
    :return: dictionary {(long, lat) : number of check-ins}.
    """
    client = foursquare.Foursquare(client_id='FUG50WOUTS2FHTCUIVFUUXFFTUGGIC1CITI53KBXPAVDFDV0',
                                   client_secret='2BLM42NTYGLNAA0J3ECOZSHJVJ0ZBC1S32MWBF24JWDN5PIX')
    checkins = client.venues.explore(params={'near': 'New York, NY', 'afterTimestamp': date})

    dict = {}

    for checkin in checkins['groups']:
        for item in checkin['items']:
            lat = item['venue']['location']['lat']
            lng = item['venue']['location']['lng']
            cic = item['venue']['stats']['checkinsCount']
            dict[(lng, lat)] = cic

    return dict


def getTaxiTrips(date):
    """
    Gets the taxi trips occurred in NY from a starting date.
    :param date: (Y-m-d).
    :return: list of tuples (long, lat, drop off date).
    """
    today = date.split('-')
    today_y = today[0]
    today_m = today[1]

    start = date.split('-')
    start_y = start[0]
    start_m = start[1]

    dicts = []
    for y in range(int(start_y), int(today_y)+1):
        for m in range(int(start_m), int(today_m)+1):
            # Month transformation
            mt = str(m) if m > 9 else '0'+str(m)

            # Green cabs
            data = readCSV("https://storage.googleapis.com/tlc-trip-data/" + str(y) +
                           "/green_tripdata_" + str(y) + "-" + mt + ".csv")
            if data is not None:
                dicts.append(data)
                print "https://storage.googleapis.com/tlc-trip-data/" + str(y) +\
                      "/green_tripdata_" + str(y) + "-" + mt + ".csv"

            # Yellow cabs
            data = readCSV("https://storage.googleapis.com/tlc-trip-data/" + str(y) +
                           "/yellow_tripdata_" + str(y) + "-" + mt + ".csv")
            if data is not None:
                dicts.append(data)
                print "https://storage.googleapis.com/tlc-trip-data/" + str(y) +\
                      "/yellow_tripdata_" + str(y) + "-" + mt + ".csv"

    points = []
    for dict in dicts:
        for line in dict:
            latitude = line.get('dropoff_latitude', None)
            if latitude is None:
                latitude = line.get('Dropoff_latitude', None)

            longitude = line.get('dropoff_longitude', None)
            if longitude is None:
                longitude = line.get('Dropoff_longitude', None)

            time = line.get('tpep_dropoff_datetime', None)
            if time is None:
                time = line.get('Lpep_dropoff_datetime', None)

            if time is not None and latitude is not None and longitude is not None and \
                            datetime.strptime(time, '%Y-%m-%d %H:%M:%S') >= datetime.strptime(date, '%Y-%m-%d'):
                points.append((longitude, latitude, time))

    return points


###################----------- Data Per Region -----------###################
def pointInPolygon(polyDict, points):
    """
    Defines which points are inside which regions.
    :param polyDict: dictionary {region id : polygon}.
    :param points: list of tuples (long, lat).
    :return: dictionaries {region id : number of points} and {region id : points}
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
                dict_points[j].append(point)

    return dict_count, dict_points


def POIsPerRegion(regions, POIs):
    """
    Defines which POIs falls in which regions.
    :param regions: dictionary {region id : polygon}.
    :param POIs: list of tuples (long, lat).
    :return: dictionaries {region id : number of POIs} and {region id : POIs' coordinates}
    """
    return pointInPolygon(regions, POIs)


def roadsNodesPerRegion(regions, nodes):
    """
    Defines which road nodes falls in which regions.
    :param regions: dictionary {region id : polygon}.
    :param nodes: list of tuples (long, lat).
    :return: dictionaries {region id : number of road nodes} and {region id : roads nodes' coordinates}.
    """
    return pointInPolygon(regions, nodes)


def roadsLenghtPerRegion(nodes_per_region_points, edges, nodes):
    """
    Obtain the total length of road bed per region.
    :param nodes_per_region_points: dictionary {region id : number of roads nodes}.
    :param edges: list of edges between nodes as tuples (long, lat).
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


def checkinsPerRegion(regions, checkins):
    """
    Obtain the total of check-ins that falls in a region.
    :param regions: dictionary {region id : polygon}.
    :param checkins: dictionary {(long, lat) : number of check-ins}.
    :return: dictionary {region id : number of check-ins}.
    """
    dict = {}

    spots_per_region_number, spots_per_region_points = pointInPolygon(regions, checkins.keys())
    for key, value in spots_per_region_points.iteritems():
        dict[key] = 0
        for v in value:
            dict[key] += checkins[v]

    return dict


if __name__ == '__main__':
    # Yesterday's date
    date = str(datetime.date(datetime.now()) - timedelta(30 * 6))
    print date

    # # Noise Categories Correlation
    # print "Getting noise complaints"
    # complaints, complaints_loc = get311NoiseComplaints(date)
    #
    # # Geographical Features
    # regions_bbox = getRegions()
    # regions_number = len(regions_bbox)
    # print "Regions:", regions_number
    #
    # print "Reading POIs..."
    # POIs = getPOIs()
    # print "POIs:", len(POIs)
    #
    # print "Calculating POIs per Region"
    # POIs_per_region = POIsPerRegion(regions_bbox, POIs)
    #
    # nodes, edges = getRoadsNodesAndEdges()
    # print "Nodes:", len(nodes)
    # print "Edges:", len(edges)
    #
    # print "Calculating roads intersections and length per Region"
    # nodes_per_region_number, nodes_per_region_points = roadsNodesPerRegion(regions_bbox, nodes)
    # roads_length_per_region = roadsLenghtPerRegion(nodes_per_region_points, edges, nodes)
    #
    # # Human Mobility Features
    # print "Getting Foursquare check-ins"
    # check_ins = getFoursquareCheckIns()
    #
    # print "Calculating check-ins per Region"
    # check_ins_per_region = checkinsPerRegion(regions_bbox, check_ins)

    print "Getting taxi data"
    taxi_dropoffs = getTaxiTrips(date)
    print len(taxi_dropoffs), "taxi trips"
