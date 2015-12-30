import numpy as np

class PointThinner(object):
    def __init__(self, percision=None):
        self._percision = percision

    def _determine_percision(self, points):
        point_range = np.amax(points) + abs(np.amin(points))
        next_val = 1000
        next_per = 0
        while True:
            if point_range > next_val:
                return next_per
            next_val = next_val / 10
            next_per = next_per + 1

    def thin(self, points):
        if self._percision is None:
            percision = self._determine_percision(points)
        else:
            percision = self._percision
        rounded = np.round(points, percision)
        contigous_points = np.ascontiguousarray(rounded).view(np.dtype((np.void, rounded.dtype.itemsize * rounded.shape[1])))
        _, points_index = np.unique(contigous_points, return_index=True)
        return points[points_index]


