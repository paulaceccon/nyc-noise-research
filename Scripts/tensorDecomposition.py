import numpy
import collections
import itertools

from haversine import haversine
from shapely.geometry import shape


def fillX(regions_bbox, intersections_per_region, length_per_region,
          POIs_abs_per_region):
    """
    Fill the X matrix for the Tensor Context Aware Decomposition.
    :param regions_bbox: bounding box of each region, necessary to calculate their areas.
    :param intersections_per_region: dictionary {region id : total road length}.
    :param length_per_region: dictionary {region id : number of POIs}.
    :param POIs_abs_per_region: dictionary {complaint category : number}.
    :return: a numpy array containing features (columns) by region (lines).
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


def fillY(taxi_dropoffs_per_region):
    """
    Fill the Y matrix for the Tensor Context Aware Decomposition.
    :param taxi_dropoffs_per_region: dictionary {region id : (long, lat, date)}.
    :return: numpy array representing the human mobility per region and time slot.
    """
    regions_count = len(taxi_dropoffs_per_region)

    Y = numpy.zeros((regions_count, 24))

    for key, value in taxi_dropoffs_per_region:
        date = datetime.strptime(value[2], '%Y-%m-%d %H:%M:%S')
        index = round(float(str(date.hour)+','+date(date.minute)))
        Y[int(key), int(index)] += 1

    return Y


def fillZ(complaints_loc, dist):
    """
    Fill the Z matrix for the Tensor Context Aware Decomposition.
    :param complaints_loc: dictionary {complaint type : [coordinates]}
    :param dist: minimum distance between coordinates to be considered.
    :return: numpy array containing the correlation between each complaint category.
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

    return Z
