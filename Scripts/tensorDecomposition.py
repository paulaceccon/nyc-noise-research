import numpy
import collections
import itertools
import scipy.io
import math

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
    
    
def contextAwareTuckerDecomposition(A, B, C, D, epsilon=0.001, lambda_1=0.0001, lambda_2=0.0001, lambda_3=0.0001, lambda_4=0.0001):
	# Size of core tensor
	dim_X = dim_Y = 10
	
	# Step size
	t = t_0 = 10
	
	dim_1, dim_2, dim_3 = A.shape
	
	# Initialize R C T S U with small random values
	X = numpy.random.rand(dim_1, dim_X) / 10
	Y = numpy.random.rand(dim_2, dim_X) / 10
	Z = numpy.random.rand(dim_3, dim_X) / 10
	S = numpy.random.rand(dim_X, dim_Y, dim_X) / 10
	U = numpy.random.rand(dim_X, B.shape[1]) / 10
	
	indices = numpy.nonzero(A)  # 3D array
	values = A[indices]			# 1D array
	turn = range(0, len(values))
	
	# Initialize function loss
	print len(values), 'non-zero elements'  # CHECKED
	c = numpy.zeros(values.shape)
	for j in range(0, len(values)):	
		ijk = numpy.tensordot(S,   X[indices[0][j],:].T, axes=([1,0])).reshape(dim_X, dim_Y) # dim_X x dim_Y
		ijk = numpy.tensordot(ijk, Y[indices[1][j],:].T, axes=([0,0]))						 # dim_X x 1
		ijk = numpy.tensordot(ijk, Z[indices[2][j],:].T, axes=([0,0]))						 # 1 x 1
		c[j] = ijk.item()					
	loss_t_1 = numpy.linalg.norm(c - values)
	loss_t = loss_t_1 + epsilon + 1
	print loss_t_1
	
	# Get the Laplacian matrices
	LC = numpy.diag(numpy.sum(C, 0)) - C
	print LC.shape  # CHECKED
	
	while loss_t - loss_t_1 > epsilon:
		old_X = X
		old_Y = Y
		old_Z = Z
		old_S = S
		
		# Optimize each element in randomized sequence
		for num in range(0, len(values)-1):
			change = numpy.random.randint(num+1, len(values))
			temp = turn[num]
			turn[num] = turn[change]
			turn[change] = temp
			
		for num in range(0, len(values)):
			if numpy.isnan(S[1,1,1]): 
				return
			
			tnum = turn[num]
			n_ita = 1/math.sqrt(float(t))
			t = t + 1
			i = indices[0][tnum]
			j = indices[1][tnum]
			k = indices[2][tnum]
			
			X_i = X[i, :].reshape(1, dim_X)
			Y_j = Y[j, :].reshape(1, dim_X)
			Z_k = Z[k, :].reshape(1, dim_X)
			
			F_ijk = numpy.tensordot(S,     X_i.T, axes=([0,0])).reshape(dim_X, dim_Y) # dim_X x dim_Y
			F_ijk = numpy.tensordot(F_ijk, Y_j.T, axes=([0,0]))						  # dim_X x 1
			F_ijk = numpy.tensordot(F_ijk, Z_k.T, axes=([0,0]))						  # 1 x 1
			
			Y_ijk = values[tnum]
			Lfy = F_ijk.item() - Y_ijk
			
			XLfy = numpy.tensordot(S,    Y_j, axes=([0,1])).reshape(dim_X, dim_Y) # dim_X x dim_Y;
			XLfy = numpy.tensordot(XLfy, Z_k, axes=([0,1]))						  # dim_X x 1
			XLfy *= (n_ita * Lfy)
			
			YLfy = numpy.tensordot(S,    X_i, axes=([0,1])).reshape(dim_X, dim_Y) # dim_X x dim_Y;
			YLfy = numpy.tensordot(YLfy, Z_k, axes=([0,1]))						  # dim_X x 1
			YLfy *= (n_ita * Lfy)
			
			ZLfy = numpy.tensordot(S,    X_i, axes=([0,1])).reshape(dim_X, dim_Y) # dim_X x dim_Y;
			ZLfy = numpy.tensordot(ZLfy, Y_j, axes=([0,1]))						  # dim_X x 1
			ZLfy *= (n_ita * Lfy)
			
			SLfy = numpy.tensordot(X_i.reshape(dim_X, 1), Y_j.reshape(dim_X, 1), axes=([1,1])).reshape(1, dim_X, dim_X) # 1, dim_X x dim_X
			SLfy = numpy.tensordot(SLfy, Z_k.reshape(dim_X, 1), axes=([0,1]))											# dim_X x dim_X x dim_X
			
			X[i, :] = ((1 - n_ita * lambda_4) * X_i.T - XLfy).T - lambda_1 * (n_ita * (numpy.dot((numpy.dot(X_i, U) - B[i, :]), U.T))) - lambda_3 * (n_ita * (numpy.dot((numpy.dot(X_i, Z.T) - D[i, :]), Z)))		
			LCY = n_ita * numpy.dot(LC, Y)
			Y[j, :] = ((1 - n_ita * lambda_4) * Y_j - YLfy.T) - lambda_2 * LCY[j, :]
			Z[k, :] = ((1 - n_ita * lambda_4) * Z_k - ZLfy.T) - lambda_3 * (n_ita * numpy.dot((numpy.dot(Z_k, X.T) - D[:, k].T), X))
			S = (1 - n_ita * lambda_4) * S - SLfy
				
			U = U - lambda_1 * n_ita * ((numpy.dot(X_i, U) - B[i, :]).T * X_i).T - n_ita * lambda_4 * U
			
		# Compute function loss
		c = numpy.zeros(values.shape)
		for j in range(0, len(values)):
			ijk = numpy.tensordot(S,   X[indices[0][j],:].T, axes=([1,0])).reshape(dim_X, dim_Y) # dim_X x dim_Y
			ijk = numpy.tensordot(ijk, Y[indices[1][j],:].T, axes=([0,0]))						 # dim_X x 1
			ijk = numpy.tensordot(ijk, Z[indices[2][j],:].T, axes=([0,0]))						 # 1 x 1
			c[j] = ijk.item()			
			
		loss_t = loss_t_1
		loss_t_1 = numpy.linalg.norm(c - values)
		print loss_t_1
		
		break;
	X = old_X
	Y = old_Y
	Z = old_Z
	S = old_S
	
	return X, Y, Z, S
	
	
if __name__ == '__main__':
	A = scipy.io.loadmat('../Resources/TensorMat/A_weekend.mat')
	B = scipy.io.loadmat('../Resources/TensorMat/B.mat')
	C = scipy.io.loadmat('../Resources/TensorMat/C_weekend.mat')
	D = scipy.io.loadmat('../Resources/TensorMat/D_weekend.mat')
	
	A = A['A'][0,0]['data']
	B = B['B']
	C = C['C']
	D = D['D'].T
	print A.shape, B.shape, C.shape, D.shape
	
	X, Y, Z, S = contextAwareTuckerDecomposition(A, B, C, D)
	T = numpy.tensordot(S, X, axes=([0,1])) # R x dim_X x dim_Y
	T = numpy.tensordot(T, Y, axes=([1,1]))	# R x C x dim_Y
	T = numpy.tensordot(T, Z, axes=([2,1]))	# R x C x T

			
		
	
	
	
	
	
