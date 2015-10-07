import numpy as np


class PointConverter(object):
    def __init__(self):
        pass

    def get_points(self, frame, center):
        roi = frame
        maxindex = np.argmax(roi, axis=1)
        data = (np.ones(maxindex.shape[0]) * center) - maxindex
        data[data == center] = -1

        return data
