import urllib2, json, csv
import numpy

from shapely.geometry import shape, Point

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
	
	
def getRegions():
	"""
	Returns a dictionary formed by the id of a region and its coordinates.
	"""
	dict = {}
	# (longitude, latitude)
	url = "https://nycdatastables.s3.amazonaws.com/2013-08-19T18:22:23.125Z/community-districts-polygon.geojson"
	data = readJson(url)
	for district in data['features']:
		dict[district['id']] = district['geometry']
		
	return dict
	
	
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
# 				print (float(longitude), float(latitude))
				POIs.append((float(latitude), float(longitude))) 
				  
	return POIs
		
			
	
def POIsInRegion(regions, POIs):
	"""
	Returns a dictionary formed by the id of a region and the number of POIs that falls in
	this region.
	"""
	dict = {}
	
	for key, value in regions.iteritems():
		dict[key] = 0	
		polygon = shape(value)
# 		print value
		for p in POIs:
			point = Point(p[0], p[1])
# 			print point
    		if polygon.contains(point):
    			dict[key] += 1
    			
	return dict
        
	
	
if __name__ == '__main__':
	 
	# Geographical Features
	regions_bbox = getRegions()
	regions_number = len(regions_bbox)
	print "Regions: ", regions_number
	
	print "Reading POIs..."
	POIs = getPOIs()
	print "Done Reading ", len(POIs), " POIs"
	
	print "Calculating POIs per Region"
	POIsPerRegion = POIsInRegion(regions_bbox, POIs)
	print POIsPerRegion
	
	
	
