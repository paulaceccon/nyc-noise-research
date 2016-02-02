import numpy
import collections
import scipy.io
import math

from haversine import haversine
from datetime import datetime, timedelta


def roundTime(dt=None, roundTo=60):
    """
    Round a datetime object to any time laps in seconds
    :param dt: datetime.datetime object, default now.
    :param roundTo: closest number of seconds to round to, default 1 minute.
    :return: the rounded time.
    """
    if dt is None: dt = datetime.now()
    seconds = (dt - dt.min).seconds
    rounding = (seconds + roundTo / 2) // roundTo * roundTo
    return dt + timedelta(0, rounding - seconds, -dt.microsecond)


def fillA(regions_bbox, complaints_region_hour, complaints_loc):
    """
    Fill the A matrix for the Tensor Context Aware Decomposition.
    :param regions_bbox: bounding box of each region, necessary to calculate their areas.
    :param complaints_region_hour: dictionary {region id : (long/lat, hour, complaint type)}.
    :param complaints_loc: dictionary {complaint type : (long/lat, hour, complaint type)}.
    :return: a numpy array containing the number complaints by region (line), type (column)
    and hour (depth).
    """
    regions_count = len(regions_bbox)
    complaints_type_count = len(complaints_loc)

    complaints_loc = collections.OrderedDict(sorted(complaints_loc.items()))  # To maintain an order in a dict

    A = numpy.zeros((regions_count, complaints_type_count, 24))

    for key, value in complaints_region_hour.iteritems():
        r = key
        for complaints in value:
            t = complaints[2]
            c = complaints_loc.keys().index(complaints[3])
            A[r, c, t] += 1

    # Normalization
    max = numpy.amax(A)
    A = A / max if max > 0 else 0
    return A, max


def fillX(regions_bbox, intersections_per_region, length_per_region, POIs_per_region):
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
    for key, value in POIs_per_region.iteritems():
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

    # Normalization
    X[:, 0] = X[:, 0] / numpy.amax(X[:, 0]) if numpy.amax(X[:, 0]) > 0 else 0
    X[:, 1] = X[:, 1] / numpy.amax(X[:, 1]) if numpy.amax(X[:, 1]) > 0 else 0
    X[:, 2] = X[:, 2] / numpy.amax(X[:, 2]) if numpy.amax(X[:, 2]) > 0 else 0
    X[:, 3] = X[:, 3] / numpy.amax(X[:, 3]) if numpy.amax(X[:, 3]) > 0 else 0
    return X


def fillY(taxi_dropoffs_per_region):
    """
    Fill the Y matrix for the Tensor Context Aware Decomposition.
    :param taxi_dropoffs_per_region: dictionary {region id : (long, lat, hour)}.
    :return: numpy array representing the human mobility per region and time slot.
    """
    regions_count = len(taxi_dropoffs_per_region)

    Y = numpy.zeros((regions_count, 24))

    for key, value in taxi_dropoffs_per_region.iteritems():
        for dropoff in value:
            Y[int(key), int(dropoff[2])] += 1

    # Normalization
    Y = Y / numpy.amax(Y) if numpy.amax(Y) > 0 else 0
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
                    for l2 in loc_2:
                        p1 = (l1[0], l1[1])
                        p2 = (l2[0], l2[1])
                        if haversine(p1, p2) <= dist:  # Distance between two complaints of types *i* and *j*
                            sum += 1
                mul = float(len(loc_1) * len(loc_2))
                if mul != 0:
                    Z[index_1, index_2] = sum / mul  # Correlation between category *i* and *j*
                else:
                    Z[index_1, index_2] = 0.0

    return Z


def contextAwareTuckerDecomposition(A, B, C, D, epsilon=0.001, lambda_1=0.0001, lambda_2=0.0001, lambda_3=0.0001,
                                    lambda_4=0.0001, validation=False):
    # Size of core tensor
    dim_X = dim_Y = 10

    # Step size
    t_0 = 10
    t = t_0

    dim_1, dim_2, dim_3 = A.shape  # CHECKED

    # Initialize R C T S U with small random values

    if not validation:
        X = numpy.random.random((dim_1, dim_X), dtype=numpy.float64) / 10.0
        Y = numpy.random.random((dim_2, dim_X), dtype=numpy.float64) / 10.0
        Z = numpy.random.random((dim_3, dim_X), dtype=numpy.float64) / 10.0
        S = numpy.random.random((dim_X, dim_Y, dim_X), dtype=numpy.float64) / 10.0
        U = numpy.random.random((dim_X, B.shape[1]), dtype=numpy.float64) / 10.0  # CHECKED
    else:
        X = scipy.io.loadmat('../Resources/TensorMat/Xrand.mat', mat_dtype=True)['X']
        Y = scipy.io.loadmat('../Resources/TensorMat/Yrand.mat', mat_dtype=True)['Y']
        Z = scipy.io.loadmat('../Resources/TensorMat/Zrand.mat', mat_dtype=True)['Z']
        S = scipy.io.loadmat('../Resources/TensorMat/Srand.mat', mat_dtype=True)['S'][0, 0]['data']
        U = scipy.io.loadmat('../Resources/TensorMat/Urand.mat', mat_dtype=True)['U']
        print X.shape, Y.shape, Z.shape, S.shape, U.shape  # CHECKED
        print X.dtype, Y.dtype, Z.dtype, S.dtype, U.dtype

    indices = numpy.nonzero(A)  # 3D array
    indices = numpy.sort(indices)  # CHECKED
    values = A[indices[0], indices[1], indices[2]]  # 1D array  # CHECKED
    turn = range(0, len(values))  # CHECKED

    # Initialize function loss
    print values.shape, 'non-zero elements'  # CHECKED

    c = numpy.zeros(values.shape, dtype=numpy.float64)
    for j in range(0, len(values)):
        ijk = numpy.tensordot(S, X[indices[0][j], :].T, axes=([0, 0])).reshape(dim_X, dim_Y)  # dim_X x dim_Y
        ijk = numpy.tensordot(ijk, Y[indices[1][j], :].T, axes=([0, 0]))  # dim_X x 1
        ijk = numpy.tensordot(ijk, Z[indices[2][j], :].T, axes=([0, 0]))  # 1 x 1
        c[j] = ijk.item()

    loss_t_1 = numpy.linalg.norm(c - values)
    loss_t = loss_t_1 + epsilon + 1  # CHECKED
    print loss_t_1  # CHECKED

    # Get the Laplacian matrices
    LC = numpy.diag(numpy.sum(C, 0)) - C  # CHECKED

    while abs(loss_t - loss_t_1) > epsilon:
        old_X = X
        old_Y = Y
        old_Z = Z
        old_S = S

        # Optimize each element in randomized sequence
        for num in range(0, len(values) - 1):
            change = num + 1  # numpy.random.randint(num+1, len(values))
            temp = turn[num]
            turn[num] = turn[change]
            turn[change] = temp  # CHECKED

        for num in range(0, len(values)):
            if numpy.isnan(S[1, 1, 1]):
                return

            tnum = turn[num]
            n_ita = 1 / math.sqrt(float(t))
            t += 1
            i = indices[0][tnum]  # CHECKED
            j = indices[1][tnum]  # CHECKED
            k = indices[2][tnum]  # CHECKED

            X_i = numpy.copy(X[i, :]).reshape(dim_X, 1)  # CHECKED
            Y_j = numpy.copy(Y[j, :]).reshape(dim_X, 1)  # CHECKED
            Z_k = numpy.copy(Z[k, :]).reshape(dim_X, 1)  # CHECKED

            F_ijk = numpy.tensordot(S, X_i.T, axes=([0, 1])).reshape(dim_X, dim_Y)  # dim_X x dim_Y  #  CHECKED
            F_ijk = numpy.tensordot(F_ijk, Y_j.T, axes=([0, 1]))  # dim_X x 1
            F_ijk = numpy.tensordot(F_ijk, Z_k.T, axes=([0, 1]))  # 1 x 1

            Y_ijk = values[tnum]  # CHECKED
            Lfy = F_ijk.item() - Y_ijk  # CHECKED

            XLfy = numpy.tensordot(S, Y_j, axes=([2, 0])).reshape(dim_X, dim_Y)  # dim_X x dim_Y;  #  CHECKED
            XLfy = numpy.tensordot(XLfy, Z_k, axes=([1, 0]))  # dim_X x 1
            XLfy *= (n_ita * Lfy)

            YLfy = numpy.tensordot(S, Z_k, axes=([2, 0])).reshape(dim_X, dim_Y)  # dim_X x dim_Y;  #  CHECKED
            YLfy = numpy.tensordot(YLfy, X_i, axes=([0, 0]))  # dim_X x 1
            YLfy *= (n_ita * Lfy)

            ZLfy = numpy.tensordot(S, Y_j, axes=([1, 0])).reshape(dim_X, dim_Y)  # dim_X x dim_Y;  #  CHECKED
            ZLfy = numpy.tensordot(ZLfy, X_i, axes=([0, 0]))  # dim_X x 1
            ZLfy *= (n_ita * Lfy)

            SLfy = numpy.tensordot(X_i, Y_j, axes=[1, 1]).reshape(1, dim_X, dim_X)  # 1, dim_X x dim_X  #  CHECKED
            SLfy = numpy.tensordot(SLfy, Z_k, axes=[0, 1])
            SLfy *= (n_ita * Lfy)

            X[i, :] = ((1 - n_ita * lambda_4) * X_i - XLfy).T - lambda_1 * (
                n_ita * (numpy.dot((numpy.dot(X_i.T, U) - B[i, :]), U.T))) - lambda_3 * (
                n_ita * (numpy.dot((numpy.dot(X_i.T, Z.T) - D[i, :]), Z)))            # CHECKED
            LCY = n_ita * numpy.dot(LC, Y)                                            # CHECKED
            Y[j, :] = ((1 - n_ita * lambda_4) * Y_j - YLfy).T - lambda_2 * LCY[j, :]  # CHECKED
            Z[k, :] = ((1 - n_ita * lambda_4) * Z_k - ZLfy).T - lambda_3 * (
                n_ita * numpy.dot((numpy.dot(Z_k.T, X.T) - D[:, k].T), X))            # CHECKED
            S = (1 - n_ita * lambda_4) * S - SLfy                                     # CHECKED
            U = U - lambda_1 * n_ita * ((numpy.dot(X_i.T, U) - B[i, :]).T * X_i.T).T - n_ita * lambda_4 * U

        # Compute function loss
        c = numpy.zeros(values.shape, dtype=numpy.float64)
        for j in range(0, len(values)):
            ijk = numpy.tensordot(S,   X[indices[0][j], :].T, axes=([0,0])).reshape(dim_X, dim_Y)  # dim_X x dim_Y
            ijk = numpy.tensordot(ijk, Y[indices[1][j], :].T, axes=([0,0]))						   # dim_X x 1
            ijk = numpy.tensordot(ijk, Z[indices[2][j], :].T, axes=([0,0]))						   # 1 x 1
            c[j] = ijk.item()
        loss_t = loss_t_1
        loss_t_1 = numpy.linalg.norm(c - values)
        print loss_t_1

    X = old_X
    Y = old_Y
    Z = old_Z
    S = old_S

    return X, Y, Z, S


if __name__ == '__main__':
    A = scipy.io.loadmat('../Resources/TensorMat/A_weekend.mat', mat_dtype=True)
    B = scipy.io.loadmat('../Resources/TensorMat/B.mat', mat_dtype=True)
    C = scipy.io.loadmat('../Resources/TensorMat/C_weekend.mat', mat_dtype=True)
    D = scipy.io.loadmat('../Resources/TensorMat/D_weekend.mat', mat_dtype=True)
    m = scipy.io.loadmat('../Resources/TensorMat/MAX_weekend.mat', mat_dtype=True)

    A = A['A'][0, 0]['data']
    B = B['B']
    C = C['C']
    D = D['D'].T
    m = m['MAX'][0, 0]
    print A.shape, B.shape, C.shape, D.shape

    X, Y, Z, S = contextAwareTuckerDecomposition(A, B, C, D, validation=True)
    T = numpy.tensordot(S, X, axes=([0, 1]))  # R x dim_X x dim_Y
    T = numpy.tensordot(T, Y, axes=([1, 1]))  # R x C x dim_Y
    T = numpy.tensordot(T, Z, axes=([0, 1]))  # R x C x T
    T = T * m
    scipy.io.savemat('T.mat', {'T': T})
    print T