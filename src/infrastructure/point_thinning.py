import numpy as np

class PointThinner(object):
    def __init__(self):
        pass

    def thin(self, points, percision):
        rounded = np.round(points, percision)
        contigous_points = np.ascontiguousarray(rounded).view(np.dtype((np.void, rounded.dtype.itemsize * rounded.shape[1])))
        _, points_index = np.unique(contigous_points, return_index=True)
        return points[points_index]


