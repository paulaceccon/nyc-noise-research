import numpy
import collections
import itertools

from haversine import haversine
from shapely.geometry import shape


def fillX(regions_bbox, intersections_per_region, length_per_region,
          POIs_abs_per_region):
    """
    Fill the X matrix for the Tensor Context Aware Decomposition.
    @regions_bbox contains the bounding box, necessary to calculate each region area.
    @intersections_per_area is a dictionary in the form id : number of intersections.
    @length_per_region is a dictionary in the form id : total road length.
    @POIs_abs_per_region is a dictionary in the form id : number of POIs.
    @POIs_category_per_region is a dictionary in the form id :[{category : number}].
    """
    regions_count = len(regions_bbox)

    X = numpy.zeros((regions_count, 4))

    # Number of road intersections per region
    for key, value in intersections_per_region.iteritems():
        X[int(key), 0] = value

    # Total road length per region
    for key, value in length_per_region.iteritems():
        X[int(key), 1] = value

    # Number/Density of POIs per region
    for key, value in POIs_abs_per_region.iteritems():
        # Number
        X[int(key), 2] = value
        # Area
        area = regions_bbox[key].area
        X[int(key), 3] = value / area

    # Distribution of POIs per region
    # 	for key, value in POIs_category_per_region:
    # 		od = collections.OrderedDict(sorted(value.items()))
    # 		for i, v in enumerate(od.values()):
    # 			X[int(key), 4+i] = v

    return X


def fillZ(complaints_loc, dist):
    """
    Given a dictionary of complaints categories : coordinates of each complaint and a
    distance @dist, returns a correlation matrix between each complaint category.
    """
    complaints_loc = collections.OrderedDict(sorted(complaints_loc.items()))  # To maintain an order in a dict
    categories = len(complaints_loc)  # Number of different categories

    Z = numpy.ones((categories, categories))

    for index_1, key_1 in enumerate(complaints_loc):
        for index_2, key_2 in enumerate(complaints_loc):
            if index_1 != index_2:
                loc_1 = complaints_loc[key_1]  # List of tuples corresponding to coordinates for type *i*
                loc_2 = complaints_loc[key_2]  # List of tuples corresponding to coordinates for type *j*
                sum = 0
                for l1 in loc_1:
                    count = 0
                    for l2 in loc_2:
                        if haversine(l1, l2) <= dist:  # Distance between two complaints of types *i* and *j*
                            count += 1
                    sum += count
                Z[index_1, index_2] = sum / float(len(loc_1) * len(loc_2))  # Correlation between category *i* and *j*
